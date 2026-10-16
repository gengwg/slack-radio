from slack_radio.slack import fetch_unreads

USERS = {"ME": "Me", "U1": "Alice", "U2": "Bob", "UB": "Grafana"}
CHANNELS = {
    "C1": {"id": "C1", "name": "general", "last_read": "100"},
    "D1": {"id": "D1", "is_im": True, "user": "U2", "last_read": "100"},
    "C2": {"id": "C2", "name": "quiet", "last_read": "100"},
    "C3": {"id": "C3", "name": "ext-ops-prod", "last_read": "100"},
    "D2": {"id": "D2", "is_im": True, "user": "U1", "last_read": "0000000000.000000"},
}
HISTORY = {
    "C1": [
        {"ts": "103", "user": "U1", "text": "third"},
        {"ts": "102", "subtype": "channel_join", "user": "U2", "text": "joined"},
        {"ts": "101", "user": "ME", "text": "my question", "reply_count": 1},
    ],
    "D1": [{"ts": "105", "user": "U2", "text": "hi", "files": [{"title": "a.pdf"}]}],
    "C2": [],
    "C3": [{"ts": "107", "user": "U1", "text": "server report"}],
    "D2": [{"ts": "90", "user": "U1", "text": "first ever"}],
}
REPLIES = {
    "101": [
        {"ts": "101", "user": "ME"},
        {"ts": "104", "user": "U2", "text": "answer"},
    ]
}


class FakeSlack:
    """In-memory stand-in for the Slack Web API methods we call."""

    def auth_test(self):
        return {"user_id": "ME", "team_id": "T1"}

    def users_info(self, user):
        return {
            "user": {
                "name": user.lower(),
                "profile": {"display_name": USERS[user]},
            }
        }

    def users_conversations(self, **kw):
        return [{"channels": [{"id": c} for c in CHANNELS]}]

    def conversations_info(self, channel):
        return {"channel": CHANNELS[channel]}

    def conversations_history(self, channel, oldest, limit):
        assert oldest != "0000000000.000000", "Slack rejects this: invalid_ts_oldest"
        return {"messages": [m for m in HISTORY[channel] if m["ts"] > (oldest or "")]}

    def conversations_replies(self, channel, ts, oldest, limit):
        return {"messages": REPLIES[ts]}


def test_fetch_unreads():
    team, convs, name_of = fetch_unreads(FakeSlack(), skip=["ext-*"])
    assert team == "T1"
    assert [(c.kind, c.name) for c in convs] == [
        ("im", "Bob"),
        ("im", "Alice"),
        ("channel", "general"),
    ]

    dm, never_opened, general = convs
    assert [m.text for m in never_opened.messages] == ["first ever"]
    assert (dm.messages[0].text, dm.messages[0].files) == ("hi", ["a.pdf"])
    # My own message is kept only because someone replied in its thread.
    # Joins and bot posts are dropped.
    assert [(m.author, m.text) for m in general.messages] == [
        ("Me", "my question"),
        ("Alice", "third"),
    ]
    assert [(r.author, r.text) for r in general.messages[0].replies] == [
        ("Bob", "answer")
    ]
    assert name_of("U1") == "Alice"


def test_fetch_unreads_without_skip_includes_all_channels():
    _, convs, _ = fetch_unreads(FakeSlack())
    assert "ext-ops-prod" in [c.name for c in convs]
