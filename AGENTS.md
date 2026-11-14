# Working in slack-radio

## Current implementation

- `src/slack_radio/__init__.py` is the CLI pipeline; `slack.py` fetches unread Slack conversations, `speech.py` builds speakable chapters, `voices.py` assigns voices, `audio.py` renders Edge TTS and MP3 chapters, and `feed.py` writes/prunes the podcast feed.
- `tests/` uses fake Slack data and temporary output paths. `systemd/` contains the generator oneshot/timer and static Tailscale feed server; `slack-app-manifest.yaml` declares the user-token read scopes.
- Use `pyproject.toml` and `uv.lock` with `uv`. Ask before adding dependencies. `ffmpeg` and `ffprobe` are external runtime/test requirements, not Python packages.
- `PROMPT.md`, `REPORT.md`, and `docs/research/` are historical research/design material, not current architecture. In particular, the old Kokoro/local-only proposal is stale: the current implementation uses Microsoft Edge online TTS. Treat current source, tests, README, manifest, and units as authoritative.

## Offline checks

Run from the repository root using the existing environment:

```sh
uv run --offline pytest -q --deselect=tests/test_audio.py::test_render_with_real_tts
uv run --offline ruff check .
uv run --offline ruff format --check .
```

The real-TTS test contacts Microsoft and must never run as part of a broad/default test command. Keep it deselected unless the user separately approves that live operation; do not run an unfiltered pytest command. The remaining audio test exercises local `ffmpeg`/`ffprobe` only.

If the existing uv environment cannot run these checks offline, report the missing capability rather than installing/updating dependencies or silently dropping `--offline`.

## Runtime effects and private files

- Both CLI modes are live Slack reads. `--dry-run` still needs the user token, fetches current unread messages, and prints private message text to the terminal; it skips TTS, voice persistence, feed writes, and pruning. It is not an offline preview.
- A normal run reads Slack, sends message/chapter text to Microsoft through `edge-tts`, updates `voices.json`, writes MP3 episodes and `feed.xml`, and prunes episodes older than three days before rendering. It does not mark Slack messages read. Require explicit approval before either live mode or a systemd generation run, and make the Microsoft data flow clear when proposing cloud-TTS changes.
- `.env`, `voices.json`, and `out/` are intentionally ignored local/private state. The voice file contains Slack identities, while episodes contain work messages. Never commit, publish, or paste real tokens, message text, voice mappings, feed URLs with secret path components, or generated audio into docs/tests/tickets. Use synthetic test data.
- Pruning deletes `*.mp3` files under the selected output's `episodes/` directory. Do not point commands at unrelated output directories or manually delete/prune user artifacts without confirmation.

## Voice persistence invariant

`voices.POOL` is ordered and append-only: never reorder, remove, or insert entries. Persisted `voices.json` choices take precedence over defaults and support manual overrides. Per-episode collision resolution may choose a temporary free voice but must not rewrite those saved choices. Preserve the tests in `tests/test_voices.py` for all three behaviors.

## Feed and deployment cautions

- The feed and audio are private but the static HTTP server provides no authentication. Use the random `SLACK_RADIO_OUT`/`SLACK_RADIO_BASE_URL` path and parent index described in the README; an unguessable path is not access control.
- Bind only to the intended Tailscale address and restrict firewall/ACL access to the user's device. Do not expose the feed on a public interface, upload it to a podcast hosting service, or assume every tailnet user should have access. Podcast services that fetch feeds through their own servers can copy or fail to reach this private content.
- The units assume `~/projects/slack-radio`, uv at `~/.local/bin/uv`, `.env` with `SLACK_RADIO_OUT`, and a manually replaced `<tailscale-ip>` placeholder in the feed service. Review unit diffs and obtain approval before installing, starting, restarting, enabling a timer, or changing linger/firewall/Tailscale configuration. Keep the README, units, CLI output settings, and manifest scopes coordinated when those assumptions change.
