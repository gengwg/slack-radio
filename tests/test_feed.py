import os
import time
import xml.etree.ElementTree as ET

from slack_radio import feed


def test_prune_and_feed(tmp_path):
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    old, new = episodes / "20260101-070000.mp3", episodes / "20261008-070000.mp3"
    old.write_bytes(b"old")
    new.write_bytes(b"new!")
    stale = time.time() - 4 * 86400
    os.utime(old, (stale, stale))

    feed.prune(episodes)
    feed.write_feed(tmp_path, "http://host:8000/")

    assert not old.exists()
    items = ET.parse(tmp_path / "feed.xml").getroot().findall("channel/item")
    assert len(items) == 1
    enclosure = items[0].find("enclosure").attrib
    assert enclosure == {
        "url": "http://host:8000/episodes/20261008-070000.mp3",
        "length": "4",
        "type": "audio/mpeg",
    }
