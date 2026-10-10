# Phase 1: Existing solutions (checked 2026-10-08)

Goal: fetch all unread Slack messages, read them aloud for a commute, each author gets a distinct expressive voice.

Bottom line: nothing currently available does this end to end. The one product that matched the core idea (TeamParrot, iOS, 2017, a different voice per author) is gone from the App Store. Slack's own AI features are text only. The parts you would build from are mature: multi-speaker TTS APIs, open-source dialogue TTS models, and podcast-generator pipelines.

## Slack-specific

| Tool | What it does | Closeness | Maintained | License | Price | Use / fork |
|---|---|---|---|---|---|---|
| TeamParrot (iOS) | Reads Slack channel messages aloud, one voice per author, can mark as read after reading | High, but dead | App Store page returns 404. Only coverage found is from Apr 2017 | Proprietary | Was free | Neither. Reference only |
| Slack AI (summaries, recaps, huddle notes) | Text summaries of unread messages, last 7 days, or a custom range. Daily recaps of chosen channels | Low: text only, no audio | Active. Recaps auto-enabled Mar 2026 | Proprietary | Summaries on Pro. Recaps on Business+ | Use as the summary source if the plan allows. Not fork |
| SlackAIChat (zvone187) | Web app that pulls unread Slack messages without marking them read. GPT voice Q&A over them | Med: solves the unread fetch, but has no per-author voices or playback queue | Last push 2025-10-13, 0 stars | None (all rights reserved) | Free, needs your own OpenAI key | Read for reference. Cannot legally fork |
| HowlSlack | Bot that reads one channel aloud through AWS Polly on Raspberry Pi speakers | Low: live office announcements, not a digest | Last push 2019-01, 1 star | GPL-3.0 | Free + Polly | Not worth it |
| Wordware "Slack to Podcast" agent | Filters Slack by keyword, has an LLM write a script, TTS (11 presets) to an MP3 on RSS, Notion or Drive | Med: an audio digest, but a single narrator | Blog post dated 2025-04-30. wordware.ai now sells "Sauna" and no longer mentions the agent | Proprietary | Was "free for light usage" | Likely discontinued (unverified) |
| Zapier / IFTTT / Make + ElevenLabs/Polly | No-code flows that turn Slack events into TTS files | Low: per-event clips, no unread digest, no voice per author | Active | Proprietary | Per-platform plans | Prototyping only |
| stickyamor/brief-plugin | Claude Code plugin that summarizes Gmail and Slack and reads the summary aloud | Low-med: a summary, not a cast of voices | Push 2026-06, 0 stars | None | Free | Reference only |

Sources: https://www.addictivetips.com/ios/listen-to-slack-messages-read-aloud-from-any-channel , https://apps.apple.com/us/app/teamparrot-listen-to-your/id1148185584 (404) , https://slack.com/help/articles/25076892548883-Guide-to-AI-features-in-Slack , https://uit.stanford.edu/news/reclaim-your-time-new-slack-ai-features-arrive-march-25 , https://github.com/zvone187/SlackAIChat , https://www.producthunt.com/products/slack-ai-assistant-2 , https://github.com/HowlSlack/app , https://blog.wordware.ai/turn-your-slack-threads-into-a-podcast-meet-wordwares-slack-podcast-ai-agent , https://www.wordware.ai/ , https://www.make.com/en/integrations/slack/elevenlabs , https://github.com/stickyamor/brief-plugin

## Open-source podcast / multi-speaker pipelines and models

| Project | What it does | Closeness | Last commit | License | Stars | Use / fork |
|---|---|---|---|---|---|---|
| lfnovo/podcast-creator | Python library: content to LLM script to 1-4 speakers, each with a voice and a personality. Many LLM/TTS providers | High as the audio stage | 2026-10-04 | MIT | 130 | Use as a library or fork |
| lfnovo/open-notebook | NotebookLM clone. Podcasts with 1-4 speakers built on podcast-creator | Med: an app for documents, not Slack | 2026-10-05 (v1.15.0) | MIT | ~40k | Fork-able but large. Borrow the pattern |
| souzatharsis/podcastfy | Text, URLs or PDFs to a 2-host conversational podcast. OpenAI, Google, ElevenLabs and Edge TTS | Med: fixed 2-host format that rewrites content | Code 2025-12-09. Last release v0.4.0 (2024-11) | Apache-2.0 | 6.6k | Usable. Slowing down |
| gabrielchua/open-notebooklm | PDF to podcast (Gradio demo) | Low | 2024-12-07 | Apache-2.0 | 2.6k | Stale |
| lamm-mit/PDF2Audio | PDF to podcast/lecture with OpenAI TTS | Low | 2025-04-18 | Apache-2.0 | 1.4k | Stale |
| nari-labs/dia, dia2 | Dialogue TTS in one pass with [S1]/[S2] tags and nonverbal cues | Med: expressive but only 2 speakers, English, max ~2 min | 2025-11 | Apache-2.0 | 19k / 1.2k | Self-host option |
| resemble-ai/chatterbox | TTS with zero-shot voice cloning. Turbo/Nano support [laugh]-style tags. Nano runs about 3x realtime on 8 CPU cores | Med: good per-author voice building block | 2026-07-21 | MIT | 27k | Self-host option |
| hexgrad/kokoro | Small 82M TTS, many preset voices, fast on CPU | Med: cheap distinct voices, limited emotion | 2025-08-06 | Apache-2.0 | 9.2k | Self-host option |
| microsoft/VibeVoice | Long-form TTS, up to 4 speakers / 90 min | Low now: TTS code removed 2025-09 for misuse, 1.5B weights "Disabled". Realtime-0.5B still available | 2026-10-08 | MIT | 55k | Avoid the TTS model |
| boson-ai/higgs-audio | Expressive text-audio model with multi-speaker dialogue | Med (unverified depth) | 2026-06-05 | Apache-2.0 | 8.4k | Self-host option |
| rany2/edge-tts | Free Microsoft Edge online TTS from Python, many voices | Med: zero-cost prototype voices | 2026-03-22 | LGPL/GPL mix (GitHub: NOASSERTION) | 12k | Prototype only. Unofficial API |

Sources: https://github.com/lfnovo/podcast-creator , https://github.com/lfnovo/open-notebook , https://github.com/souzatharsis/podcastfy , https://github.com/gabrielchua/open-notebooklm , https://github.com/lamm-mit/PDF2Audio , https://github.com/nari-labs/dia , https://github.com/nari-labs/dia2 , https://github.com/resemble-ai/chatterbox , https://github.com/hexgrad/kokoro , https://github.com/microsoft/VibeVoice , https://github.com/boson-ai/higgs-audio , https://github.com/rany2/edge-tts (stars and dates from the GitHub API, 2026-10-08)

## Commercial TTS APIs (building blocks)

| API | Multi-voice / expressiveness | Price | Notes |
|---|---|---|---|
| ElevenLabs Text to Dialogue | Any number of speakers per request (a voice_id per turn). Inline tags like [whispering] and [giggling]. Models v3 and v4 | TTS v4 $0.022/1K chars (promo until Oct 12, normally $0.08). v3 $0.08. Plans start at $6/mo | 2,000 chars per request, so long text must be chunked. Closest to "radio play" out of the box |
| Google Gemini TTS | Max 2 speakers per request. Style is set per turn with natural-language prompts plus inline <sigh>-style cues. 30 featured voices plus an extended library | Not checked | For more than 2 voices, synthesize each turn separately and concatenate |
| OpenAI gpt-4o-mini-tts | One voice per request, 13 built-in voices. An `instructions` prompt controls tone and emotion. Streams | Not on docs page (unverified) | Simple per-message calls. Fewer voices than authors in a big workspace |

Sources: https://elevenlabs.io/docs/capabilities/text-to-dialogue , https://elevenlabs.io/pricing/api , https://ai.google.dev/gemini-api/docs/speech-generation , https://developers.openai.com/api/docs/guides/text-to-speech

## Listen-while-driving products

| Product | What it does | Closeness | Status | Price |
|---|---|---|---|---|
| Siri Announce Notifications (CarPlay/AirPods) | Reads incoming notifications from supported third-party apps, Slack reportedly included. Hands-free reply | Low: live, one notification at a time, Siri voice only, no backlog | Active. Slack support from press reports, not confirmed on Apple's page (unverified) | Free |
| Android Auto + Gemini | Reads and can summarize messages from Android Auto-compatible messaging apps | Low: Slack is not named as compatible (unverified) | Active | Free |
| Outlook Copilot voice catch-up | Guided voice walkthrough of important email and meetings. You can interrupt with questions and triage by voice (flag, archive, delete, draft reply) | Med on UX, wrong data source | Preview/rolling out 2026. Requires an M365 Copilot license | Copilot license |
| Outlook "Play My Emails" (Cortana) | Read email aloud, then a voice action after each one. Steering-wheel controls | Med on UX | Retired June 2024 | n/a |
| ElevenReader | Reads imported docs, PDFs and articles. 1,000+ voices | Low: no Slack/email import, no multi-voice | Active | Free 10 h/mo. Ultra $11/mo |
| Speechify | Document TTS, AI summaries, "AI Podcasts" | Low: no Slack integration listed | Active | Free. Premium $29/mo |
| Superhuman | Text one-line AI summaries. Voice input for replies | None: no read-aloud found | Active | n/a |

Sources: https://support.apple.com/en-au/108415 , https://aitopics.org/tag/announce%20notification , https://support.google.com/androidauto/answer/6348317 , https://developer.android.com/training/auto/messaging/index , https://support.microsoft.com/en-US/Outlook/catch-up-on-your-inbox-with-copilot-voice-in-outlook , https://mc.merill.net/message/RM516575 , https://support.microsoft.com/en-gb/office/how-do-i-start-using-play-my-emails-5e7bce1a-0ad9-4a79-83b3-1cce5c516c29 , https://elevenreader.io/pricing , https://speechify.com/pricing/ , https://superhuman.com/gmail-alternative

## Design ideas worth copying

- Voice per author (TeamParrot, podcast-creator). Keep a stable author-to-voice map so a colleague always sounds the same. podcast-creator's speakers_config (voice plus personality per speaker) fits this directly.
- Don't mark messages read by default (SlackAIChat). Make "mark read after playback" an opt-in setting (TeamParrot).
- Read-then-act loop (Play My Emails, Copilot voice catch-up). After each channel or thread, offer skip, mark read, or replay. Let the user interrupt to ask "what was that about?"
- Car-friendly controls: big next/prev channel buttons and a "mark all read" escape hatch (TeamParrot). Steering-wheel media keys through the Media Session API on web (Play My Emails supported steering-wheel controls).
- Two modes. Verbatim for DMs and mentions. LLM-condensed script for busy channels (Wordware, Slack recaps). Slack recaps already offer "unread / 7 days / custom range" scopes.
- Prioritize before playing: DMs and mentions first, then followed channels (Copilot voice catch-up walks through "important" items first).
- Expressiveness: let an LLM add per-line tags ([laughs], [whispering]) or a style instruction from emoji and tone. ElevenLabs v3/v4 tags, Gemini styles and OpenAI `instructions` all accept this.
- Ship a podcast/RSS output as an alternative to live playback (Wordware). It works in any car player with no app needed.
- Chunking: ElevenLabs dialogue caps at 2K chars and Gemini at 2 speakers per request, so synthesize per turn or per small group and concatenate.
