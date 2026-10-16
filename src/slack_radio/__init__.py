import argparse
import os
from datetime import datetime
from pathlib import Path

from slack_radio import audio, feed, voices
from slack_radio.slack import fetch_unreads, make_client
from slack_radio.speech import NARRATOR, build_script


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read your unread Slack messages aloud."
    )
    parser.add_argument(
        "--out", type=Path, default=Path("out"), help="directory to serve"
    )
    parser.add_argument("--voices", type=Path, default=Path("voices.json"))
    parser.add_argument("--base-url", default=os.environ.get("SLACK_RADIO_BASE_URL"))
    parser.add_argument(
        "--skip",
        default=os.environ.get("SLACK_RADIO_SKIP", ""),
        help="comma-separated channel names to leave out; * patterns allowed",
    )
    parser.add_argument("--dry-run", action="store_true", help="print the script only")
    args = parser.parse_args()
    if not (args.dry_run or args.base_url):
        parser.error("set --base-url or SLACK_RADIO_BASE_URL to where --out is served")

    client = make_client(os.environ["SLACK_USER_TOKEN"])
    skip = [s.strip().lstrip("#") for s in args.skip.split(",") if s.strip()]
    team_id, conversations, name_of = fetch_unreads(client, skip)
    chapters = build_script(conversations, name_of)

    names = {NARRATOR: "Narrator"}
    for c in conversations:
        for m in c.messages:
            for msg in [m, *m.replies]:
                names[msg.author_id] = msg.author

    if args.dry_run:
        for c in chapters:
            print(f"== {c.title}")
            for line in c.lines:
                print(f"[{names[line.speaker]}] {line.text}")
        return
    if len(chapters) == 1:
        print("No unread messages.")
        return

    speakers = {}
    for c in chapters:
        for line in c.lines:
            if line.speaker is not NARRATOR:
                speakers.setdefault(line.speaker, names[line.speaker])
    cast = voices.assign(args.voices, team_id, speakers)
    cast[NARRATOR] = voices.NARRATOR_VOICE

    episodes = args.out / "episodes"
    episodes.mkdir(parents=True, exist_ok=True)
    feed.prune(episodes)
    now = datetime.now().astimezone()
    mp3 = episodes / f"{now:%Y%m%d-%H%M%S}.mp3"
    seconds = audio.render(chapters, cast, mp3, f"Slack Radio {now:%Y-%m-%d %H:%M}")
    feed.write_feed(args.out, args.base_url)
    print(f"Wrote {mp3} ({seconds / 60:.1f} min, {len(chapters) - 1} conversations)")
