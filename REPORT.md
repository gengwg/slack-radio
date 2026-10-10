# Slack Radio: research and plan

Researched 2026-10-08. Detailed, fully cited notes are in `docs/research/`:
[existing solutions](docs/research/1-existing-solutions.md),
[Slack API](docs/research/2-slack-api.md),
[TTS, voices, privacy](docs/research/3-tts-voices-privacy.md),
[playback and text cleanup](docs/research/4-playback-and-text.md).
Items marked "unverified" there could not be confirmed in a primary source.

## TL;DR

Nothing available today reads your unread Slack aloud with a voice per author, so build it.
The simplest version that works on a commute is a small Python job you run before leaving. It
collects unread messages with a Slack user token, turns them into a script with announcements,
renders each author with a stable local Kokoro voice, and publishes one MP3 with chapters to a
private podcast feed. Your podcast app then handles offline download, lock-screen, headphone and
car controls. Slack text never leaves your machines, and the TTS costs nothing.

## Phase 1: Existing solutions

| Tool | What it is | Closeness | Maintained | License | Price |
|---|---|---|---|---|---|
| [TeamParrot](https://www.addictivetips.com/ios/listen-to-slack-messages-read-aloud-from-any-channel) | iOS app that read Slack aloud, one voice per author, could mark messages read | High, but dead | No; [App Store page](https://apps.apple.com/us/app/teamparrot-listen-to-your/id1148185584) is 404 | Proprietary | Was free |
| [Slack AI recaps/summaries](https://slack.com/help/articles/25076892548883-Guide-to-AI-features-in-Slack) | Text summaries of unread messages and channels | Low (text only) | Yes | Proprietary | Pro / Business+ |
| [SlackAIChat](https://github.com/zvone187/SlackAIChat) | Fetches unread messages without marking them read; voice Q&A over them with GPT | Medium | Last push 2025-10 | None, so you cannot fork it | Free + OpenAI |
| [Wordware Slack-to-Podcast](https://blog.wordware.ai/turn-your-slack-threads-into-a-podcast-meet-wordwares-slack-podcast-ai-agent) | LLM script from Slack, one narrator, MP3 on an RSS feed | Medium | Likely discontinued (unverified) | Proprietary | Was free |
| [HowlSlack](https://github.com/HowlSlack/app) | Bot that speaks one channel through AWS Polly | Low | 2019 | GPL-3.0 | Free |
| [lfnovo/podcast-creator](https://github.com/lfnovo/podcast-creator) | Python: content to LLM-written script to 1-4 voiced speakers | Medium (audio stage only, rewrites content) | Active (2026-10) | MIT | Free |
| [Podcastfy](https://github.com/souzatharsis/podcastfy) | Text/URL to a 2-host podcast | Low-medium | Slowing (last release 2024-11) | Apache-2.0 | Free |
| [ElevenLabs Text to Dialogue](https://elevenlabs.io/docs/capabilities/text-to-dialogue) | API: many voices per request, emotion tags | Medium (building block) | Yes | Commercial | See TTS table |
| [Siri Announce](https://support.apple.com/en-au/108415), [Android Auto](https://support.google.com/androidauto/answer/6348317) | Read live notifications in the car | Low (no backlog, one voice) | Yes | Proprietary | Free |
| [Outlook Copilot voice catch-up](https://support.microsoft.com/en-US/Outlook/catch-up-on-your-inbox-with-copilot-voice-in-outlook) | Voice walkthrough of email you can interrupt and triage by voice | Medium on UX, but email only | Rolling out 2026 | Proprietary | Copilot license |
| [ElevenReader](https://elevenreader.io/pricing), [Speechify](https://speechify.com/pricing/) | Read docs and articles aloud | Low (no Slack) | Yes | Proprietary | Free tier; $11-29/mo |

Nothing here can be used directly. The only one worth forking is podcast-creator (MIT), but it
rewrites content with an LLM, and you want messages read word for word. It isn't worth the
dependency.

Ideas to copy:
- Keep each author's voice fixed (TeamParrot).
- Don't mark messages read by default (SlackAIChat).
- Play DMs and mentions first (Copilot).
- Use one chapter per channel, so "next" means "skip channel".
- Read DMs word for word and only consider summaries for busy channels (Wordware, Slack recaps).
- Deliver as RSS so it works in any car (Wordware).

## Phase 2: Technical findings

### 1. Slack API

- **Token:** you need a user token (`xoxp`). A bot token can't see your DMs or your read
  state ([tokens](https://docs.slack.dev/authentication/tokens)).
- **Scopes:**
  - `channels:history groups:history im:history mpim:history`
  - `channels:read groups:read im:read mpim:read users:read`
  - Add `*:write` only if you want to mark messages read.
- **Install:** for a single-user app, use "Install to Workspace" in the app settings and copy
  the token. No OAuth redirect server is needed.
- **Getting unreads (all documented APIs):**
  1. [`users.conversations`](https://docs.slack.dev/reference/methods/users.conversations)
     lists your channels, DMs and group DMs.
  2. [`conversations.info`](https://docs.slack.dev/reference/methods/conversations.info)
     gives `last_read`, your read cursor.
  3. [`conversations.history`](https://docs.slack.dev/reference/methods/conversations.history)
     with `oldest=last_read` gets the new messages.
  4. [`conversations.replies`](https://docs.slack.dev/reference/methods/conversations.replies)
     gets thread replies.
  5. [`users.info`](https://docs.slack.dev/reference/methods/users.info) resolves names. Cache
     the results.
- **Known gaps:**
  - The docs show `last_read` only in a DM example, and say the unread counts are "for DM
    conversations only". Check on day 1, with a real token, that channels return `last_read`.
  - There is no official "unread threads" API. New replies on threads whose parent is older
    than your channel cursor can't be found reliably, so the MVP leaves them out.
- **Undocumented, avoid:** `client.counts`, `users.counts`, `client.boot`, `subscriptions.thread.*`
  (all 404 on docs.slack.dev). `channel_marked`/`im_marked` events exist only on the RTM API,
  which [new apps can't use](https://docs.slack.dev/legacy/legacy-rtm-api).
- **Marking read:** [`conversations.mark`](https://docs.slack.dev/reference/methods/conversations.mark)
  is Tier 3 and works with a user token. There is no API to mark a thread read.
- **Rate limits:** Tier 3 (50+/min) for history, replies, info, mark and users.conversations;
  Tier 4 for users.info ([rate limits](https://docs.slack.dev/apis/web-api/rate-limits)). The
  May 2025 cut to 1 request/min and 15 messages per call applies only to apps distributed
  commercially outside the Marketplace. Slack says "Internal customer-built applications are not
  impacted" ([changelog](https://docs.slack.dev/changelog/2025/05/29/rate-limit-changes-for-non-marketplace-apps)).
  Keep the app internal to your workspace.
- **Admin approval:** not needed by default; members can install apps themselves. You need
  approval if an owner turned on app approval, or if an Enterprise Grid org has an app
  policy ([approval](https://slack.com/help/articles/222386767-Manage-app-approval-for-your-workspace),
  [Grid](https://slack.com/help/articles/360038559694-Set-organization-level-policies-for-apps)).
- **Terms:** the [API Terms](https://slack.com/terms-of-service/api) (Oct 2025) ban training
  LLMs on API data and bulk export. Reading messages aloud is fine. Don't store message
  archives.

### 2. Text to speech

Cost per hour of audio, assuming 150 words/min, which is about 54,000 characters:

| Option | English voices | Expressiveness | $/hour | License / terms |
|---|---|---|---|---|
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (local) | 28 (about 16 good) plus [voice blending](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py) | Low: no emotion control | $0, runs on CPU | Apache-2.0 |
| [Piper](https://github.com/OHF-Voice/piper1-gpl) (local) | 900+ speakers in one model | None (flat) | $0, CPU | GPL-3.0 code |
| [Kyutai Pocket TTS](https://github.com/kyutai-labs/pocket-tts) (local) | 26 plus voice cloning | Follows the reference voice | $0, ~2.5x real time on 4 vCPU | MIT / CC-BY (some voices non-commercial) |
| [Chatterbox](https://github.com/resemble-ai/chatterbox) (local) | Voice cloning only | Exaggeration knob, `[laugh]` tags | $0, CPU (Nano) | MIT, adds a watermark |
| [OpenAI gpt-4o-mini-tts](https://developers.openai.com/api/docs/guides/text-to-speech) | 13 | High: free-text `instructions` for tone and emotion | ~$0.91 (unverified token rate) | Commercial |
| [Google Chirp 3 HD / Gemini TTS](https://cloud.google.com/text-to-speech/pricing) | 30 | Gemini: style prompts, at most 2 speakers per call | $0.91-1.81 | Commercial |
| [Azure Neural / HD](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices) | ~60 neural, 700+ multilingual HD | SSML styles; HD picks emotion up from the text | $0.81 / $1.19 | Commercial |
| [ElevenLabs v4 + Text to Dialogue](https://elevenlabs.io/pricing/api) | Thousands | Highest: tags, multi-speaker dialogue | $2.16-4.32 at list price | Commercial |

All of these are fine for pre-rendered audio, so latency doesn't matter. Kokoro is the best
local default: Apache license, small and fast, enough distinct voices. Its weakness is flat
emotion. OpenAI is the cheapest step up in expressiveness, and ElevenLabs is the most "radio
play" but costs 2-5x more and has privacy downsides (see below).

### 3. Stable voice per person

1. Reserve one voice as the narrator.
2. Pick each author's default voice as
   `pool[int(sha256(team_id+user_id)) % len(pool)]` over an ordered, curated pool. Don't use
   Python's `hash()`, which is salted per process.
3. Save the first assignment to `voices.json`. The file wins from then on, so adding voices
   later doesn't remap anyone, and you can edit it to override.
4. Collisions are likely: with 5 authors and 28 voices, the chance two share a voice is about
   30%. In each episode, a later author who would share a voice gets the next free one for that
   episode only.

### 4. Listenability

- Walk the [`rich_text`](https://docs.slack.dev/reference/block-kit/blocks/rich-text-block)
  blocks and fall back to the [mrkdwn](https://docs.slack.dev/messaging/formatting-message-text)
  `text`:
  - Mentions become display names, and `<#C|name>` becomes "hash name".
  - Links become "link to github.com".
  - Code blocks become "code snippet, N lines".
  - Emoji are dropped; an emoji-only message is skipped.
  - Files become "shared a file: name".
  - Joins, leaves and deletes are skipped; edited messages are read in their latest version.
- Announce the channel ("In hash deploys, 4 new messages") and the speaker when it changes
  ("Alice:"), and merge back-to-back messages from the same person. Insert silence: about
  300 ms between messages and 1 s between channels.
- Threads: read the parent, then the replies. Summarizing with an LLM would shorten long threads,
  but it adds another processor of your data and can misattribute speakers. Leave it out of the
  MVP, and if added later, label the output "Summary".

### 5. Commute playback

| | Web / PWA | Native app | Private podcast feed |
|---|---|---|---|
| Plays with screen locked | Android OK. iOS home-screen app has open WebKit bugs ([261858](https://bugs.webkit.org/show_bug.cgi?id=261858), [291892](https://bugs.webkit.org/show_bug.cgi?id=291892)) | Reliable | Reliable |
| Lock screen / headphones / car | [Media Session](https://web.dev/articles/media-session); no CarPlay or Android Auto | Full, but CarPlay/AA need extra approval | Full, done by the app, plus speed and resume |
| Offline | Service worker cache; iOS can evict it; no Background Fetch on iOS | Full | App downloads episodes automatically |
| Effort | Medium, plus iOS testing pain | High | Low: MP3 + `feed.xml` + static host |

The podcast feed wins for the MVP. Put one chapter per channel in the MP3 as
[ID3 CHAP](https://id3.org/id3v2-chapters-1.0) frames, so chapter skip works as "next channel".
Which phone you use matters:
- [AntennaPod](https://antennapod.org/documentation/general/central-distributed) (Android)
  fetches the feed from the phone itself, so the feed can stay on Tailscale or your LAN.
- Overcast and Pocket Casts fetch feeds through their own servers
  ([Overcast](https://overcast.fm/podcasterinfo),
  [Pocket Casts](https://support.pocketcasts.com/knowledge-base/password-protected-podcasts/)),
  so with those, use an unguessable URL and keep titles generic.

A web app is a reasonable later step if you want in-app actions such as "mark this channel read".

### 6. Privacy

Risks of cloud TTS:
- Work messages are processed and stored by a vendor your company may not have approved.
- Some vendors train on your content by default.
- Logs are kept for a while.
- It may breach your employer's data policy. Check this before using any cloud TTS.

| Provider | Trains by default | Retention | Zero-retention option |
|---|---|---|---|
| [OpenAI](https://developers.openai.com/api/docs/guides/your-data) | No | Abuse logs for 30 days | Yes, by approval through sales |
| [ElevenLabs](https://elevenlabs.io/docs/resources/zero-retention-mode) | Yes, unless you [opt out](https://elevenlabs.io/terms-of-use) | History saved by default | Enterprise only |
| [Google Cloud TTS](https://cloud.google.com/text-to-speech/docs/data-logging) | No | "Does not log" Cloud TTS text/audio; unclear for Gemini-TTS | Can disable the Gemini cache |
| [Azure Speech](https://learn.microsoft.com/en-us/legal/cognitive-services/speech-service/text-to-speech/data-privacy-security) | Not stated | Real-time prebuilt voices: text and audio not logged | Real-time already doesn't log |

The options, from most to least private:
- local TTS (no data leaves);
- Azure real-time or Google Cloud TTS (no logging);
- OpenAI (30-day logs, ZDR by request);
- ElevenLabs (opt out of training, Enterprise needed for zero retention).

The episode MP3 also contains the messages, so keep the feed private and delete old episodes
automatically.

## Phase 3: Recommendation and plan

**Decision: build our own.** Nothing existing covers the core: unread Slack, a voice per author,
playable offline. Each piece needs only a little glue code: Slack's documented API, Kokoro, and
a standard podcast feed. Forking podcast-creator or Podcastfy would bring in an LLM rewriting
step and a fixed host format that you don't want.

**MVP architecture.** One Python script (uv), run by cron or by hand before leaving:

```
slack_radio.py
  fetch      users.conversations -> conversations.info (last_read)
             -> conversations.history + conversations.replies -> users.info
  script     normalize text, order DMs -> group DMs -> channels, add announcements
  voices     voices.json (sha256 default, editable)
  render     Kokoro per line -> concatenate with silences -> ffmpeg MP3 -> ID3 chapters per channel
  publish    out/<random-token>/episode-<date>.mp3 + feed.xml (generic titles), delete episodes after 3 days
phone: podcast app subscribed to https://<host>/<random-token>/feed.xml
```

There is no database, server code or web UI. Hosting is any static file server you already have,
or `uv run python -m http.server` behind Tailscale.

**Proposed dependencies (need your OK):** `slack-sdk`, `kokoro`, which pulls in PyTorch (about a
2 GB install with the CPU wheel), `soundfile`, and `mutagen` for ID3 chapters. System packages:
`ffmpeg` and `espeak-ng`, which Kokoro needs for unknown words.

**One-week MVP:**
1. Create the Slack app, get a token, and fetch unreads for channels, DMs and group DMs, including
   thread replies under unread parents. Check `last_read` on channels.
2. Normalize the text and add announcements. Print the script as text so you can review it before
   any audio exists.
3. Build the Kokoro voice pool and `voices.json`, then render one MP3 with chapters.
4. Set up the feed and hosting, subscribe on your phone, and test it on a real commute.

Out of the MVP: marking messages read, summaries, cloud TTS, a web UI, live mode, and new replies on
old threads.

**Later, roughly in order of value:**
1. Optional OpenAI `gpt-4o-mini-tts` backend with per-person tone instructions, for more
   expressive voices.
2. A "mark what I heard as read" command that calls `conversations.mark` up to the newest
   rendered `ts` of each channel.
3. Allow and deny lists for channels, and a maximum episode length.
4. Labelled LLM summaries for threads over N messages.
5. Track new replies on older threads with a local per-thread cursor.
6. A web/PWA player if you want in-app actions.

## Open questions for you

1. iPhone or Android, and which podcast app? This decides whether the feed can stay private on
   Tailscale or your LAN.
2. Should listening mark messages as read? The options are never (the MVP), as soon as the
   episode is generated, or a manual "mark heard" command afterwards. A podcast app can't tell us
   what you actually listened to.
3. Which channels: every channel you're in, or an allow/deny list? Should bot messages be
   included?
4. Budget and policy: is $0 local TTS with flatter voices acceptable, or is about $1/hour for
   cloud TTS worth it? Does your employer allow sending Slack content to OpenAI, Google, Azure or
   ElevenLabs?
5. Is your workspace on Enterprise Grid, or does it need app approval? If so, request approval
   for a user-token app early.
6. Where should generation run (laptop, home server), and where will the feed be hosted?
7. What's the longest episode you want, and what should happen when unreads exceed it: truncate
   oldest, or skip big channels?
8. Are the proposed dependencies OK (`slack-sdk`, `kokoro` + PyTorch, `soundfile`, `mutagen`,
   plus `ffmpeg` and `espeak-ng`)?
