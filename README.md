# Slack Radio

Reads your unread Slack messages aloud as a podcast episode, with a distinct voice per person.
Bot messages are skipped and nothing is marked as read.

## Setup

1. Create a Slack app from `slack-app-manifest.yaml` at https://api.slack.com/apps
   ("From a manifest"), click "Install to Workspace", and copy the User OAuth Token.
2. Create `.env`:

   ```
   SLACK_USER_TOKEN=xoxp-...
   SLACK_RADIO_BASE_URL=http://<this-machine-ip>:8000
   SLACK_RADIO_SKIP=ext-ops-*,alerts   # optional: channels to leave out, * patterns allowed
   ```

3. Serve the output directory on your home Wi-Fi or Tailscale IP:

   ```
   uv run python -m http.server 8000 --bind <this-machine-ip> -d out
   ```

## Use

```
uv run --env-file .env slack-radio --dry-run   # print the script
uv run --env-file .env slack-radio             # write out/episodes/*.mp3 and out/feed.xml
```

## Phone (Android)

1. With the phone on the same Wi-Fi, open `$SLACK_RADIO_BASE_URL/feed.xml` in its browser. If it
   times out, open the firewall: `sudo ufw allow from <lan-subnet> to any port 8000 proto tcp`.
2. In AntennaPod: Add podcast > Add podcast by RSS address > the same URL. Spotify can't add RSS
   feeds by URL.

Each morning, while the phone is still on home Wi-Fi:

```
uv run python -m http.server 8000 --bind <this-machine-ip> -d out   # if not already running
uv run --env-file .env slack-radio                                  # ~2.5 min
```

Then refresh the feed in AntennaPod (it checks only every 12 hours) and let the episode download.
It plays offline. Chapter skip moves to the next conversation. Episodes older than 3 days are
deleted.

Voices are saved in `voices.json`; edit a `voice` to change how someone sounds
(list voices with `uv run edge-tts --list-voices`).

TTS uses Microsoft Edge's online voices via `edge-tts`, so message text is sent to Microsoft.
