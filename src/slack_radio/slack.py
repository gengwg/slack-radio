from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from fnmatch import fnmatch
from functools import cache

from slack_sdk import WebClient
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

TYPES = "im,mpim,private_channel,public_channel"
KEEP_SUBTYPES = {None, "file_share", "thread_broadcast", "me_message"}
MAX_PER_CONVERSATION = 100


@dataclass
class Message:
    author_id: str
    author: str
    text: str
    files: list[str] = field(default_factory=list)
    replies: list["Message"] = field(default_factory=list)


@dataclass
class Conversation:
    kind: str  # "im", "mpim" or "channel"
    name: str
    messages: list[Message]


def make_client(token: str) -> WebClient:
    client = WebClient(token=token)
    client.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=5))
    return client


def fetch_unreads(
    client: WebClient, skip: Sequence[str] = ()
) -> tuple[str, list[Conversation], Callable[[str], str]]:
    """Return (team_id, conversations with unread messages DMs first, user name lookup)."""
    me = client.auth_test()
    my_id = me["user_id"]

    @cache
    def user(uid: str) -> dict:
        return client.users_info(user=uid)["user"]

    def user_name(uid: str) -> str:
        u = user(uid)
        return u["profile"].get("display_name") or u.get("real_name") or u["name"]

    def to_message(m: dict, keep_mine: bool = False) -> Message | None:
        if m.get("subtype") not in KEEP_SUBTYPES or m.get("bot_id") or "user" not in m:
            return None
        if (m["user"] == my_id and not keep_mine) or user(m["user"]).get("is_bot"):
            return None
        files = [
            f.get("title") or f.get("name") or "untitled" for f in m.get("files", [])
        ]
        return Message(m["user"], user_name(m["user"]), m.get("text", ""), files)

    conversations = []
    for page in client.users_conversations(
        types=TYPES, exclude_archived=True, limit=200
    ):
        for c in page["channels"]:
            info = client.conversations_info(channel=c["id"])["channel"]
            if any(fnmatch(info.get("name", ""), pattern) for pattern in skip):
                continue
            last_read = info.get("last_read")
            if not last_read:
                continue
            # Never-opened conversations report "0000000000.000000", which Slack rejects
            # as `oldest`; everything in them is unread.
            if not last_read.strip("0."):
                last_read = None
            history = client.conversations_history(
                channel=c["id"], oldest=last_read, limit=MAX_PER_CONVERSATION
            )["messages"]
            messages = []
            for m in reversed(history):
                replies = []
                if m.get("reply_count"):
                    thread = client.conversations_replies(
                        channel=c["id"], ts=m["ts"], oldest=last_read, limit=200
                    )["messages"]
                    replies = [
                        r for x in thread if x["ts"] != m["ts"] and (r := to_message(x))
                    ]
                # Keep my own thread parent when others replied to it.
                msg = to_message(m, keep_mine=bool(replies))
                if msg:
                    msg.replies = replies
                    messages.append(msg)
            if not messages:
                continue
            if info.get("is_im"):
                kind, name = "im", user_name(info["user"])
            elif info.get("is_mpim"):
                # Named like "mpdm-alice--bob--carol-1".
                kind = "mpim"
                name = ", ".join(info["name"][5:].rsplit("-", 1)[0].split("--"))
            else:
                kind, name = "channel", info["name"]
            conversations.append(Conversation(kind, name, messages))

    order = {"im": 0, "mpim": 1, "channel": 2}
    conversations.sort(key=lambda c: order[c.kind])
    return me["team_id"], conversations, user_name
