# Slack Radio

Reads your unread Slack messages aloud as a podcast episode, with a distinct voice per person.
Bot messages are skipped and nothing is marked as read.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) and ffmpeg (`sudo apt install ffmpeg`).
2. Create a Slack app from `slack-app-manifest.yaml` at https://api.slack.com/apps
   ("From a manifest"), click "Install to Workspace", and copy the User OAuth Token.
3. Create `.env`:

   ```
   SLACK_USER_TOKEN=xoxp-...
   SLACK_RADIO_BASE_URL=http://<this-machine-ip>:8000
   SLACK_RADIO_SKIP=ext-ops-*,alerts   # optional: channels to leave out, * patterns allowed
   ```

## Use

```
uv run --env-file .env slack-radio --dry-run   # print the script
uv run --env-file .env slack-radio             # write out/episodes/*.mp3 and out/feed.xml
uv run python -m http.server 8000 --bind <this-machine-ip> -d out
```

Subscribe to `$SLACK_RADIO_BASE_URL/feed.xml` in AntennaPod (Android: Add podcast > Add podcast
by RSS address; Spotify can't add RSS feeds by URL). Refresh the feed before you leave and let the
episode download; it then plays offline. Chapter skip moves to the next conversation. Episodes
older than 3 days are deleted.

The phone must reach the server, either on the same Wi-Fi (office Wi-Fi often blocks this) or
over Tailscale. Test by opening the feed URL in the phone's browser; if it times out on Wi-Fi, open
the firewall: `sudo ufw allow from <lan-subnet> to any port 8000 proto tcp`.

## Always-on server with Tailscale and systemd

On a machine that stays on, with the phone and that machine in the same tailnet:

1. Use a random path so other tailnet users can't guess the feed URL. In `.env`:

   ```
   SLACK_RADIO_BASE_URL=http://<tailscale-ip>:8000/<random>
   SLACK_RADIO_OUT=out/<random>
   ```

   Generate `<random>` with `uv run python -c "import secrets; print(secrets.token_urlsafe(16))"`,
   then `mkdir -p out && touch out/index.html` to hide the directory listing.
2. Make sure the phone can reach port 8000. If the tailnet's access rules only allow SSH between
   your devices, add one: source `autogroup:member`, destination `autogroup:self`, port
   `tcp:8000`. If ufw is on, allow only the phone:
   `sudo ufw allow in on tailscale0 from <phone-tailscale-ip> to any port 8000 proto tcp`.
3. Install the units. They expect the repo at `~/projects/slack-radio`; edit `<tailscale-ip>` in
   `slack-radio-feed.service` first.

   ```
   cp systemd/* ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now slack-radio-feed.service slack-radio.timer
   loginctl enable-linger   # keep them running when logged out
   ```

The timer generates an episode at 07:00 and 17:00 on weekdays; edit `slack-radio.timer` to
change that. Run one now with `systemctl --user start slack-radio.service`.

## Voices

Voices are saved in `voices.json`; edit a `voice` to change how someone sounds
(list voices with `uv run edge-tts --list-voices`).

TTS uses Microsoft Edge's online voices via `edge-tts`, so message text is sent to Microsoft.
