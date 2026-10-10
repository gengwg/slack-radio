import time
from datetime import UTC, datetime
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

KEEP_DAYS = 3


def prune(episodes: Path, keep_days: int = KEEP_DAYS) -> None:
    cutoff = time.time() - keep_days * 86400
    for mp3 in episodes.glob("*.mp3"):
        if mp3.stat().st_mtime < cutoff:
            mp3.unlink()


def write_feed(out: Path, base_url: str) -> None:
    """Write out/feed.xml listing out/episodes/*.mp3, newest first.

    Titles are deliberately generic: some podcast apps fetch feeds through their servers.
    """
    items = []
    for mp3 in sorted((out / "episodes").glob("*.mp3"), reverse=True):
        when = datetime.fromtimestamp(mp3.stat().st_mtime, UTC)
        url = escape(f"{base_url.rstrip('/')}/episodes/{mp3.name}")
        items.append(f"""    <item>
      <title>Slack Radio {when.astimezone():%a %b %d %H:%M}</title>
      <guid isPermaLink="false">{mp3.stem}</guid>
      <pubDate>{format_datetime(when)}</pubDate>
      <enclosure url="{url}" length="{mp3.stat().st_size}" type="audio/mpeg"/>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Slack Radio</title>
    <link>{escape(base_url)}</link>
    <description>Unread Slack messages, read aloud.</description>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (out / "feed.xml").write_text(feed)
