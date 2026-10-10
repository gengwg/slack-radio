import json

from slack_radio import voices


def test_assign_is_stable_and_persisted(tmp_path):
    path = tmp_path / "voices.json"
    first = voices.assign(path, "T1", {"U1": "Alice"})
    again = voices.assign(path, "T1", {"U1": "Alice"})
    assert first == again == {"U1": voices.default_voice("T1", "U1")}
    assert json.loads(path.read_text()) == {
        "U1": {"name": "Alice", "voice": first["U1"]}
    }


def test_manual_override_wins(tmp_path):
    path = tmp_path / "voices.json"
    path.write_text(json.dumps({"U1": {"name": "Alice", "voice": "en-GB-SoniaNeural"}}))
    assert voices.assign(path, "T1", {"U1": "Alice"}) == {"U1": "en-GB-SoniaNeural"}


def test_collisions_get_distinct_voices_without_changing_saved(tmp_path):
    path = tmp_path / "voices.json"
    same = {"name": "x", "voice": voices.POOL[0]}
    path.write_text(json.dumps({"U1": same, "U2": same, "U3": same}))
    cast = voices.assign(path, "T1", {"U1": "a", "U2": "b", "U3": "c"})
    assert cast == {"U1": voices.POOL[0], "U2": voices.POOL[1], "U3": voices.POOL[2]}
    assert all(
        v["voice"] == voices.POOL[0] for v in json.loads(path.read_text()).values()
    )
