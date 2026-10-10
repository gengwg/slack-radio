import html
import re
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urlparse

from slack_radio.slack import Conversation, Message

NARRATOR = None

NameOf = Callable[[str], str]

CODE_BLOCK = re.compile(r"```(.*?)```", re.DOTALL)
ANGLE = re.compile(r"<([^<>]+)>")
EMOJI_CODE = re.compile(r":(?=[^:\s]*[a-z])[a-z0-9_+'-]+:")
EMOJI_CHAR = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]")
URL = re.compile(r"https?://\S+")
MD_LINK = re.compile(r"\[([^\]]+)\]\(<?https?://[^)>]+>?\)")
MAX_MESSAGE_CHARS = 400


def _spoken(name: str) -> str:
    return re.sub(r"[-_]+", " ", name)


def _angle(match: re.Match, name_of: NameOf) -> str:
    body = match.group(1)
    target, _, label = body.partition("|")
    if target.startswith("@"):
        return label or name_of(target[1:])
    if target.startswith("#"):
        return f"channel {_spoken(label)}" if label else "a channel"
    if target.startswith("!"):
        if target.startswith(("!subteam", "!date")):
            return label
        return f"at {target[1:]}"
    if target.startswith("mailto:"):
        return label or target[7:]
    host = urlparse(target).hostname or "a website"
    return f"{label} (link to {host})" if label else f"link to {host}"


def speakable(text: str, name_of: NameOf) -> str:
    """Turn Slack mrkdwn into plain text that reads well aloud."""

    def code(m: re.Match) -> str:
        n = len(m.group(1).strip().splitlines())
        return f" (code snippet, {n} line{'s' if n != 1 else ''}) "

    text = CODE_BLOCK.sub(code, text)
    text = MD_LINK.sub(r"\1", text)
    text = ANGLE.sub(lambda m: _angle(m, name_of), text)
    text = URL.sub(lambda m: f"link to {urlparse(m.group(0)).hostname}", text)
    text = EMOJI_CODE.sub("", text)
    text = EMOJI_CHAR.sub("", text)
    text = re.sub(r"^&gt;\s?", "Quote: ", text, flags=re.MULTILINE)
    text = re.sub(r"[*~`]|(?<!\w)_|_(?!\w)", "", text)
    text = html.unescape(text)
    return " ".join(text.split())


def _sentence(text: str) -> str:
    return text if text[-1] in ".!?" else text + "."


def _message_text(m: Message, name_of: NameOf) -> str:
    text = speakable(m.text, name_of)
    if len(text) > MAX_MESSAGE_CHARS:
        text = text[:MAX_MESSAGE_CHARS].rsplit(" ", 1)[0] + "... Message cut short"
    parts = [text]
    parts += [f"Shared a file: {f}" for f in m.files]
    return " ".join(_sentence(p) for p in parts if p)


@dataclass
class Line:
    speaker: str | None  # Slack author ID, or NARRATOR
    text: str


@dataclass
class Chapter:
    title: str
    lines: list[Line]


def _say(lines: list[Line], speaker: str | None, text: str) -> None:
    # Merge consecutive lines from the same speaker into one TTS call.
    if lines and lines[-1].speaker == speaker:
        lines[-1].text += " " + text
    else:
        lines.append(Line(speaker, text))


def _read(
    lines: list[Line], m: Message, name_of: NameOf, previous: str | None
) -> str | None:
    """Add one message, announcing the author on speaker change. Returns the last speaker."""
    text = _message_text(m, name_of)
    if not text:
        return previous
    if m.author_id != previous:
        _say(lines, NARRATOR, f"{m.author} says:")
    _say(lines, m.author_id, text)
    return m.author_id


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def build_script(conversations: list[Conversation], name_of: NameOf) -> list[Chapter]:
    chapters = []
    for c in conversations:
        lines: list[Line] = []
        previous = None
        if c.kind == "im":
            title = f"DM from {c.name}"
            _say(lines, NARRATOR, f"Direct message from {c.name}.")
            first = c.messages[0]
            previous = first.author_id if first.author == c.name else None
        elif c.kind == "mpim":
            title = f"Group DM: {c.name}"
            _say(lines, NARRATOR, f"Group message with {c.name}.")
        else:
            title = f"#{c.name}"
            _say(lines, NARRATOR, f"In channel {_spoken(c.name)}.")
        for i, m in enumerate(c.messages):
            previous = _read(lines, m, name_of, previous)
            if m.replies:
                n = len(m.replies)
                _say(
                    lines,
                    NARRATOR,
                    f"Thread, {n} new {'reply' if n == 1 else 'replies'}.",
                )
                previous = None
                for r in m.replies:
                    previous = _read(lines, r, name_of, previous)
                if i < len(c.messages) - 1:
                    _say(lines, NARRATOR, "Back in the conversation.")
                    previous = None
        if any(line.speaker is not NARRATOR for line in lines):
            chapters.append(Chapter(title, lines))

    total = sum(
        len(c.messages) + sum(len(m.replies) for m in c.messages) for c in conversations
    )
    if not chapters:
        intro_text = "Slack Radio. You're all caught up."
    else:
        intro_text = (
            f"Slack Radio. {_plural(total, 'unread message')} "
            f"in {_plural(len(chapters), 'conversation')}."
        )
    return [Chapter("Intro", [Line(NARRATOR, intro_text)])] + chapters
