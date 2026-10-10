# Phase 2: Commute playback and speech normalization

Researched 2026-10-08. "Unverified" marks claims not confirmed in a primary source.

## A1. Web app / PWA

**Media Session API.** Supported in Chrome (desktop 73, Android 57) and Safari 15+ (iOS mirrors Safari), including `play`, `pause`, `nexttrack`, `previoustrack`, `seekforward`, `seekbackward`, `seekto` (Safari 15, Chrome 78) and `stop` ([MDN BCD data](https://github.com/mdn/browser-compat-data/blob/main/api/MediaSession.json), [MDN setActionHandler](https://developer.mozilla.org/en-US/docs/Web/API/MediaSession/setActionHandler)). MDN marks it "Limited availability" and advises try/catch around unsupported actions. Per web.dev, lock-screen controls appear on mobile, and headset buttons trigger actions. Chrome only shows a media notification for media at least 5 s long, and Android artwork should be 512x512 ([web.dev](https://web.dev/articles/media-session)). Bluetooth AVRCP and car head units are not mentioned in either source. They most likely work through the OS media session, but that is unverified.

**Background audio, screen locked.**
- Android Chrome: a plain `<audio>` element plus Media Session gives notification and lock-screen controls ([web.dev](https://web.dev/articles/media-session)). Continued playback with the screen locked is widely observed but not stated explicitly there (unverified).
- iOS Safari tab: `<audio>` keeps playing in the background in Safari. The bugs below are specific to standalone mode ([WebKit 198277](https://bugs.webkit.org/show_bug.cgi?id=198277)).
- iOS Home Screen web app: there is a long history of failures.
  - [198277](https://bugs.webkit.org/show_bug.cgi?id=198277) (2019): audio stops when a standalone app leaves the foreground. It was closed as a duplicate of [232909](https://bugs.webkit.org/show_bug.cgi?id=232909) (AVAudioSession process-assertion fix, landed Nov 2021), but commenters reported mixed results on iOS 15.x.
  - [261858](https://bugs.webkit.org/show_bug.cgi?id=261858), still NEW: on iOS 16/17 in a standalone app, the next track does not autoplay after the current one ends while locked or backgrounded, and lock-screen controls stop responding. The same page works in Safari.
  - [291892](https://bugs.webkit.org/show_bug.cgi?id=291892), still NEW: on iOS 26.0 a PWA goes silent after returning from the background, for both Web Audio and `<audio>`. One reporter says iOS 26.2 beta 3 fixed it.
  - Web Audio (`AudioContext`) is treated as ambient and gets suspended in the background ([198277 comments](https://bugs.webkit.org/show_bug.cgi?id=198277), [231105](https://bugs.webkit.org/show_bug.cgi?id=231105)), so use `<audio>`, not Web Audio.
- Mitigation: render the whole commute as one long MP3 so there are no track transitions, use chapters or seek for "next", and prefer a Safari tab over the installed PWA on iOS. Whether that is reliable on iOS 26 is unverified, so test on a device.

**Offline storage.**
- Service worker + Cache API can store the MP3s.
- Safari 17+ quotas: one origin may use up to 60% of disk in a browser app (15% in other apps). The overall cap is 80% (20%). Eviction is LRU by origin under storage pressure or after inactivity, and is best-effort unless `navigator.storage.persist()` is granted. Being a Home Screen web app is one of the heuristics for granting persistence ([WebKit storage policy](https://webkit.org/blog/14403/updates-to-storage-policy/)).
- ITP deletes all script-writable storage, including SW registrations and Cache, after 7 days of Safari use without interaction with the site. Home Screen web apps "have their own counter of days of use" and are not expected to be wiped ([WebKit ITP post](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)). A daily commute counts as interaction, so the 7-day cap rarely matters here.
- Range requests for cached audio must be handled by the service worker itself. This is a known pitfall (unverified here).

**Background Fetch.** Chrome 74+ including Android, not supported in Safari ([MDN BCD](https://github.com/mdn/browser-compat-data/blob/main/api/BackgroundFetchManager.json), [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Background_Fetch_API), experimental). On iOS, the page must be open to download.

## A2. Native

**iOS.**
- Set the `AVAudioSession` category to `.playback` and enable the Background Modes capability "Audio, AirPlay, and Picture in Picture" (`UIBackgroundModes: audio`). The default session is silenced by the ring/silent switch and by locking ([Apple](https://developer.apple.com/documentation/avfoundation/configuring-your-app-for-media-playback)).
- Lock-screen and Control Center metadata goes through [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter). Headphone, lock-screen and car buttons go through [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter) (play/pause/next/previous/skip interval/changePlaybackRate).
- CarPlay: a browsable audio app needs a CarPlay entitlement request plus approval and must follow the CarPlay review guidelines ([Apple](https://developer.apple.com/documentation/carplay/requesting-carplay-entitlements)). Without the entitlement, the Now Playing screen probably still controls the app (unverified).

**Android.**
- Media3 `MediaSessionService` hosting an ExoPlayer `MediaSession`. Declare it in the manifest with `foregroundServiceType="mediaPlayback"` and request the `FOREGROUND_SERVICE` and `FOREGROUND_SERVICE_MEDIA_PLAYBACK` permissions.
- The MediaStyle notification is automatic. System controls, Bluetooth and Assistant connect as MediaControllers. Media button resumption needs `MediaButtonReceiver` ([Android](https://developer.android.com/media/media3/session/background-playback)).
- Android Auto needs `MediaLibraryService`/`MediaBrowserService` with a browsable/playable tree and must meet the car app quality guidelines ([Android](https://developer.android.com/training/cars/media)).

Effort: two codebases plus app store review, or one cross-platform app. Background playback is reliable, but this is the most work.

## A3. Simplest: private podcast RSS feed

Generate `feed.xml` plus one MP3 per commute (with chapters). Any podcast app then provides offline download, lock-screen, headphone and car controls, speed control and resume for free.

**Adding a private feed by URL.**
- Apple Podcasts: on Mac, File > Add a Show by URL ([Apple](https://support.apple.com/guide/podcasts/follow-or-unfollow-shows-podf17151dc/mac)). On iPhone, Library > More > "Follow a Show by URL" (the menu path comes from search results, unverified). Such shows are fetched "directly from the hosting provider, not the Apple Podcasts catalog" ([Apple Podcasters](https://podcasters.apple.com/support/5108-how-apple-podcasts-distributes-your-shows-to-listeners)). Basic-auth support is unverified.
- Overcast: Add URL. It treats basic-auth URLs as private, excluding them from search and sharing. It uses **server-side crawling** of the RSS, but audio downloads directly and is not re-hosted ([Overcast](https://overcast.fm/podcasterinfo)). The in-app "Use Password" field comes from third-party guides (unverified).
- Pocket Casts: "does not formally support password-protected feeds", with "limited support" for basic auth via `https://user:pass@host/...`. Submit the feed as Private at pocketcasts.com/submit ([Pocket Casts](https://support.pocketcasts.com/knowledge-base/password-protected-podcasts/)). This is server-side as well.
- AntennaPod (Android): distributed, so the app fetches feeds from the device and passes credentials straight to the host. The default refresh is every 12 h ([AntennaPod](https://antennapod.org/documentation/general/central-distributed)). Because fetching happens on the device, a feed behind Tailscale or the LAN works. Manual refresh before leaving avoids the 12 h lag.

**Chapters.**
- `<podcast:chapters url="..." type="application/json+chapters"/>` goes once per `<item>` ([Podcasting 2.0](https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/chapters.md)).
- ID3v2 CHAP/CTOC frames embed chapters in the MP3 itself ([id3.org](https://id3.org/id3v2-chapters-1.0)). Overcast displays MP3/M4A chapter markers ([Overcast](https://overcast.fm/podcasterinfo)).
- Embedding ID3 CHAP gives the widest coverage, but support in Apple Podcasts and Pocket Casts is unverified. Make one chapter per channel so "next chapter" acts as "skip channel".

**Auth and privacy.**
- Use an unguessable URL token, for example `/feed/<128-bit random>.xml` with per-episode random filenames, or basic auth where the app supports it.
- Central crawlers (Overcast, Pocket Casts, possibly Apple) see the feed XML. Keep titles and show notes generic ("Slack digest 2026-10-08 08:00") and never put message text in RSS.
- The MP3 contains Slack content. Over HTTPS it goes to the device directly in Overcast's case; for the others it is unverified.
- Expire episodes after N days.

**Even simpler.** Drop the MP3 into a folder that syncs to the phone (Syncthing on Android, or a cloud drive) and play it in any audio player. Background and lock-screen controls depend on the player. VLC is a likely option, and the iOS Files app preview is unverified for background playback. There are no new-episode notifications and no chapters unless the player reads ID3 CHAP.

## Comparison

| | Web / PWA | Native app | Podcast feed | Synced MP3 |
|---|---|---|---|---|
| Background, locked | Android good; iOS Safari tab OK, iOS PWA buggy (198277/261858/291892) | Reliable | Reliable (app's job) | Depends on player |
| Lock screen / headphones | Media Session (Chrome 73, Safari 15) | Full (MPRemoteCommandCenter / Media3) | Full, plus speed and resume | Depends on player |
| Car (BT / CarPlay / AA) | BT likely via OS session (unverified); no CarPlay/AA app | Needs entitlement / MediaLibraryService | Podcast apps already support CarPlay and AA | Player-dependent |
| Offline | SW + Cache; iOS eviction risk; no Background Fetch on iOS | Full control | App auto-downloads | Sync tool |
| Chapters / skip channel | Build it yourself | Build it yourself | podcast:chapters / ID3 CHAP | ID3 CHAP if supported |
| Effort | Medium, with iOS testing pain | High | Low: RSS + MP3 + static host | Lowest |
| Privacy | Own server only | Own server only | Feed metadata seen by crawler apps | Sync provider |

## B. Making Slack text listenable

Syntax comes from [Slack formatting](https://docs.slack.dev/messaging/formatting-message-text), [message subtypes](https://docs.slack.dev/reference/events/message) and [rich_text](https://docs.slack.dev/reference/block-kit/blocks/rich-text-block).

| Input | Speak as |
|---|---|
| `<@U123>` | Display name (cache `users.info`) |
| `<#C123\|name>` / `<#C123>` | "hash name" or "channel name" |
| `<!here>` `<!channel>` `<!everyone>` | "at here" or drop; optionally flag the message as "urgent" |
| `<!subteam^ID>` | Group handle |
| `<!date^ts^fmt\|fallback>` | Fallback text, or spoken date |
| `<https://x/y\|label>` | Label, then "(link to x)". Bare URL becomes "link to github.com" |
| `&amp; &lt; &gt;` | Unescape first |
| `*b*` `_i_` `~s~` `` `c` `` | Strip markers; inline code is read as-is if short, else "code" |
| ```` ```block``` ```` / `rich_text_preformatted` | "Code snippet omitted, N lines" |
| `>` quote / `rich_text_quote` | "Quoting: ..." |
| Lists | Read items with short pauses |
| `:emoji:` / rich_text `emoji` (name, unicode) | Drop in mid-text. An emoji-only message becomes "reacted with thumbs up" or is skipped |
| Reactions | Skip |
| `file_share` | "Shared a file: name.pdf" (title only) |
| `bot_message` | "Bot name posted: ..." or filter by allowlist |
| `message_changed` | Read the latest text only; skip the event itself |
| `message_deleted` | Skip; `hidden` records are not for display |
| `channel_join/leave/topic/...` | Skip |
| `thread_broadcast` | Read once, in the thread context |

Prefer walking `rich_text` blocks, which carry typed user, channel, link and emoji elements, over regexing `text`. Use `text` as the fallback.

**Announcement format.**
- Channel intro: "In hash deploys, 4 new messages."
- Speaker change: "Alice says: ...".
- Consecutive messages from the same speaker within a few minutes get merged without re-announcing.
- DMs: "Direct message from Bob."
- Give relative times only when the gap is large ("an hour later").

**Threads.**
- Read the parent, then "N replies". Read replies in full when N is small (3 or fewer); otherwise read the first and last, or only the unread ones.
- Fetch with `conversations.replies`. Since 2025-05-29 it is limited to 1 request/minute (limit 15) for new non-Marketplace distributed apps. Internal apps keep Tier 3 ([Slack](https://docs.slack.dev/reference/methods/conversations.replies)), so build this as an internal app.

**LLM summary of long threads.**
- Pro: much shorter listening time for long threads.
- Con: another third-party processor of workspace data, which may conflict with workspace policy or Slack API terms (unverified). It can also hallucinate decisions or misattribute speakers.
- Middle ground: summarize only threads over N messages, label the result "Summary:", keep speaker names, offer verbatim as the default, and use a local model if policy requires it.

**SSML / pauses.** SSML 1.1 provides `<break time|strength>`, `<prosody rate|pitch|volume>`, `<say-as interpret-as>` and `<sub alias>` ([W3C SSML 1.1](https://www.w3.org/TR/speech-synthesis11/)). Engine support varies (unverified per engine). If the TTS has no SSML, put chapter and speaker boundaries in sentence punctuation or insert silence when concatenating audio segments, for example 300 ms between messages and 1 s between channels.
