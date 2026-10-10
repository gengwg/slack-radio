from slack_radio.slack import Conversation, Message
from slack_radio.speech import NARRATOR, build_script, speakable

NAMES = {"U1": "Alice", "U2": "Bob"}.__getitem__


def test_speakable_mentions_links_and_channels():
    text = "<@U1> see <https://github.com/x/y|the PR> in <#C1|deploys> and <https://example.com/a>"
    assert speakable(text, NAMES) == (
        "Alice see the PR (link to github.com) in channel deploys and link to example.com"
    )


def test_speakable_strips_formatting_emoji_and_code():
    text = "*Bold* _it_ ~gone~ `x` :tada: \U0001f680 at 10:30:45\n```a\nb\nc```\n&gt; quoted &amp; done"
    assert speakable(text, NAMES) == (
        "Bold it gone x at 10:30:45 (code snippet, 3 lines) Quote: quoted & done"
    )


def test_speakable_markdown_links_and_channel_names():
    text = "see [#3851](<https://x.grafana.net/a>) in <#C1|ext-acme---prod_1>"
    assert speakable(text, NAMES) == "see #3851 in channel ext acme prod 1"


def test_long_messages_are_cut_short():
    conv = Conversation("im", "Alice", [msg("U1", "word " * 200)])
    _, chapter = build_script([conv], NAMES)
    text = chapter.lines[-1].text
    assert len(text) < 450
    assert text.endswith("word... Message cut short.")


def test_speakable_special_mentions():
    assert speakable("<!here> <!subteam^S1|@oncall> <!date^1|Feb 18>", NAMES) == (
        "at here @oncall Feb 18"
    )
    assert speakable("snake_case_name", NAMES) == "snake_case_name"


def msg(uid, text, **kw):
    return Message(uid, NAMES(uid), text, **kw)


def test_build_script_channel_with_thread():
    conv = Conversation(
        "channel",
        "deploys",
        [
            msg("U1", "Deploying now", replies=[msg("U2", "ok"), msg("U2", "done")]),
            msg("U1", ":thumbsup:"),
            msg("U1", "All good"),
        ],
    )
    intro, chapter = build_script([conv], NAMES)
    assert intro.lines[0].text == "Slack Radio. 5 unread messages in 1 conversation."
    assert chapter.title == "#deploys"
    assert [(line.speaker, line.text) for line in chapter.lines] == [
        (NARRATOR, "In channel deploys. Alice says:"),
        ("U1", "Deploying now."),
        (NARRATOR, "Thread, 2 new replies. Bob says:"),
        ("U2", "ok. done."),
        (NARRATOR, "Back in the conversation. Alice says:"),
        ("U1", "All good."),
    ]


def test_build_script_dm_skips_redundant_announcement_and_reads_files():
    conv = Conversation("im", "Bob", [msg("U2", "", files=["plan.pdf"])])
    _, chapter = build_script([conv], NAMES)
    assert [(line.speaker, line.text) for line in chapter.lines] == [
        (NARRATOR, "Direct message from Bob."),
        ("U2", "Shared a file: plan.pdf."),
    ]


def test_build_script_drops_empty_conversations():
    conv = Conversation("channel", "random", [msg("U1", ":wave:")])
    chapters = build_script([conv], NAMES)
    assert [c.title for c in chapters] == ["Intro"]
    assert chapters[0].lines[0].text == "Slack Radio. You're all caught up."
