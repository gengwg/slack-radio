I want to build an app (web app first, maybe a phone app later) that finds all my
unread Slack messages and reads them out loud, so I can listen to them on my commute.
Each person who wrote a message should get their own distinct, expressive voice, so it
sounds like a radio play or a TV show rather than one flat narrator.

Do research and planning only. Don't write code until I approve a plan.

## Phase 1: Research existing solutions

Search the web for existing tools that do this or something close:
- Slack apps or bots that read messages aloud or turn them into audio or podcasts
- Open-source projects (GitHub etc.) that turn chat or Slack into speech, or generate
  multi-voice audio from text
- Commercial products for listening to messages, email or news while driving

For each one, give: what it does, how close it is to my goal, whether it's maintained,
the license, and the price. Tell me if any can be used directly, or forked if the license
allows. Note design ideas worth copying, such as playback controls, how it summarizes,
or how it assigns voices.

## Phase 2: Technical research

Answer these from primary sources (official docs) and cite them:
1. Slack API: how do I reliably get unread messages across channels, DMs and threads?
   Which token type and scopes does that need, and what are the rate limits? Do I need
   workspace admin approval to install a custom app? Point out any undocumented or
   unsupported APIs; I want to avoid those.
2. Text to speech: compare services that offer many distinct, natural voices (for
   example ElevenLabs, OpenAI TTS, Google, Azure) with local or open-source models (for
   example Kokoro, Piper). Cover voice quality, how many voices there are, emotion and
   expressiveness, cost per hour of audio, latency, and license.
3. How to give each Slack user a stable, distinct voice (the same person always sounds
   the same).
4. How to make it listenable: handle emoji, links, code blocks, @mentions and threads;
   add short announcements like "In #channel, Alice says..."; and decide whether to
   summarize long threads.
5. Commute use: background playback with the phone locked, lock-screen and headphone
   controls, and offline listening (generate the audio before I leave, then play it).
   Compare a web app or PWA with a native app for this.
6. Privacy: my work Slack messages would go to a third-party TTS service. List the
   risks and the options, such as local TTS or provider data-retention settings.

## Phase 3: Recommendation and plan

- Decide: use something existing, fork it, or build our own. Explain why in a few
  sentences.
- Give the simplest architecture that works for an MVP (a minimal working version).
- Describe a small MVP scope I can actually use within a week, plus a short list of
  later improvements.
- List open questions I have to answer, for example: should listening mark messages as
  read, which channels to include, and the budget.

## Constraints and preferences

- Keep it simple. No over-engineering, no extra features in the MVP.
- I mostly use Python and Go. For Python, use uv (`uv add`, `uv run`), never pip or
  requirements.txt.
- Prefer well-maintained, current libraries. Ask before adding dependencies.
- Be concise. Put findings in a short report with source links. No filler.
