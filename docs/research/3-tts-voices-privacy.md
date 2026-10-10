# Phase 2: TTS options, per-author voices, privacy

Checked 2026-10-08 against primary sources. Cost basis: 150 wpm, about 900 chars/min, so **54,000 chars per hour of audio**. Token-priced models are billed on audio duration, so their cost tracks minutes of audio, not characters.

## A. Cloud TTS

| Provider / model | English voices | Expressiveness | Price unit | Cost per hour (math) | Latency |
|---|---|---|---|---|---|
| ElevenLabs `eleven_v4` (flagship) | "Thousands", 3,000+ library voices [1] | Audio tags, multi-speaker dialogue [2] | $/1K chars | List $0.08 x 54 = **$4.32**. Promo $0.022 until Oct 12 = $1.19 [3] | Not stated [2] |
| ElevenLabs `eleven_v4_turbo` | same | Audio tags, real-time [2] | $/1K chars | List $0.04 x 54 = **$2.16** (promo $0.011 = $0.59) [3] | ~100 ms [2] |
| ElevenLabs `eleven_v3` (now "previous gen") | same | Audio tags, Text to Dialogue [2][4] | $/1K chars | $0.08 x 54 = **$4.32** [3] | Not real-time [2] |
| ElevenLabs `eleven_flash_v2_5` | same | Stability/similarity settings only, no tags [1][2] | $/1K chars | $0.04 x 54 = **$2.16** [3] | ~75 ms [2] |
| OpenAI `gpt-4o-mini-tts` (snapshot `-2025-12-15`) [6] | 13 (marin and cedar recommended) [5] | Free-text `instructions`: emotion, accent, tone, whisper, speed [5] | $0.60/1M text-in tokens, $12/1M audio-out tokens [7] | ~$0.91, **unverified**: 13.5K text tokens (4 chars/token, assumed) x $0.60/1M = $0.01, plus ~75K audio tokens x $12/1M = $0.90. Audio tokens/min is no longer published; 1,250/min is implied by OpenAI's earlier $0.015/min estimate | Streams; no numbers [5] |
| OpenAI `tts-1` / `tts-1-hd` | 9 [5] | None documented [5] | $/1M chars | $15 x 0.054 = **$0.81**. HD: $30 x 0.054 = **$1.62** [7] | tts-1 is lower latency [5] |
| Google Chirp 3 HD | 30 personas [8] | Pace, pause and pronunciation only. No style prompt [8] | $/1M chars | $30 x 0.054 = **$1.62**. First 1M chars/month free (~18.5 h) [9] | Streaming supported [8]; no numbers |
| Google Gemini-TTS `gemini-2.5-flash-tts` | Same 30 voices [10] | Natural-language style prompt plus `[sigh]`-style tags; **max 2 speakers per request** [10][11] | $0.50/1M in, $10/1M audio out at 25 tokens/s [9] | 90K audio tokens x $10/1M = $0.90, plus input ~$0.01 = **~$0.91** | "Low latency" [10] |
| Google `gemini-3.1-flash-tts-preview` | 30 (Preview) [10] | same | $1/1M in, $20/1M out [9] | 90K x $20/1M = **~$1.81** | same |
| Google Gemini 3.8 Flash TTS (Preview, Gemini Enterprise API only) [10] | 30 [11] | Adds voice design and replication [10] | $0.50 in / $9 out until 2026-12-31, then $1 / $18 [9] | 90K x $9/1M = **~$0.82**, rising to ~$1.63 in 2027 | n/a |
| Azure Neural (standard) | ~60 en-US voice names on the language page (my count) [12] | SSML `mstts:express-as` styles; which styles depends on the voice [13] | $/1M chars | $15 x 0.054 = **$0.81**. F0 tier: 0.5M chars/month free [14][15] | Not stated |
| Azure Neural HD (DragonHD / Omni / Flash) | 38 en-US HD variants [12]. Omni has 700+ voices, multilingual [16] | Detects emotion from text automatically; style tags (whispering, shouting...) and paralinguistics (laughter, sighing) [16] | $/1M chars | $22 x 0.054 = **$1.19** [15] | Not stated |

ElevenLabs Text to Dialogue (`/v1/text-to-dialogue`, models v4 and v3) takes a list of `{text, voice_id}` turns with no speaker limit. The cap is 2,000 chars per request and output is nondeterministic, though `seed` helps [4]. Of all the options, it comes closest to an actual radio play. ElevenLabs rates above are per-character API rates. Subscription plans bundle characters [3].

## A. Local / open models

| Model | English voices | Expressiveness | CPU / laptop / phone | Speed | License (code / weights / voices) |
|---|---|---|---|---|---|
| **Kokoro-82M** v1.0 [17] | 28: 20 US + 8 UK. Graded A to F, and 16 are C- or better [18] | No emotion control. Voice choice, speed, and **voice blending**, verified in code: `load_voice("af_bella,af_sarah")` averages the voice tensors (`torch.mean`) [19] | 82M params, runs on CPU (unverified RTF). ONNX build exists [20], so phones are plausible (unverified) | Not documented in primary sources | Apache-2.0 / Apache-2.0 / bundled [17][21] |
| **Piper** (`piper-tts`, OHF-Voice/piper1-gpl; rhasspy/piper archived) [22][23] | 21 en_US + 9 en_GB voice sets [24]. `en_US-libritts_r-medium` alone has **904 speakers** [25] | None (VITS, flat delivery) | ONNX Runtime on CPU, CUDA optional [26]. Phone: unverified | Not stated in current docs | **GPL-3.0** code [22]. Voices repo is MIT, but each dataset has its own license, e.g. libritts_r is CC BY 4.0 [25] |
| **Kyutai Pocket TTS** [27] | 26 pre-made, plus WAV cloning [27] | Inherits the style of the reference voice; no tags | 100M params. ~6x real-time on M4 CPU, 2.3-2.5x on 4-vCPU x86; ~200 ms to first chunk [27] | as left | MIT / CC-BY-4.0 [28] / per voice: VCTK CC-BY, donations CC0, **Expresso CC-BY-NC** [29] |
| **Chatterbox** (Resemble) [30] | No built-ins; zero-shot cloning from ~10 s clip | Original: `exaggeration` + `cfg_weight`. Turbo/Nano: `[laugh]`, `[cough]` tags | Nano (110M) targets CPU at ~3x real-time on 8 cores [30] | as left | MIT / MIT [31]. Output carries a Perth watermark [30] |
| **Dia 1.6B** (Nari) [32] | Random unless seeded or audio-prompted | `[S1]`/`[S2]` dialogue (2 speakers), (laughs), (sighs) tags | **GPU only**, ~4.4 GB VRAM bf16 [32] | 1.5-2.1x RT on RTX 4090 [32] | Apache-2.0 / Apache-2.0 [33] |

Excluded: VibeVoice. Microsoft removed the TTS code (4 speakers, 90 min) over misuse, and the model card says research-only [34]. Kyutai TTS 1.6B is GPU-class, and its CC-BY weights [28] add little over Pocket TTS for this use.

Local per-hour cost is $0 marginal. Audio can be pre-rendered before the commute, so RTF only needs to beat 1x over the batch.

## B. Stable, distinct voice per Slack author

Pool sizes (English, narrator excluded):

| Provider | Pool |
|---|---|
| OpenAI | 13 (12 after narrator). Widen it with per-user `instructions` personas, e.g. "dry, fast" or "warm, slow" |
| Google | 30 (Chirp 3 HD / Gemini). Gemini multi-speaker allows only 2 per call, so render per message |
| Azure | ~60 neural + 38 HD en-US. Omni 700+ |
| ElevenLabs | Effectively unbounded (library / voice design) |
| Kokoro | 28, ~16 good, plus unlimited blends |
| Piper | 904 in libritts_r alone, but quality per speaker varies |
| Pocket TTS | 26, plus cloning |

Design (simple, deterministic):

1. **Reserve the narrator** (channel names, "X said", timestamps). Remove it from the pool before hashing.
2. **Deterministic default**: `pool[int(sha256(team_id + user_id)) % len(pool)]`. Use a real digest, not Python `hash()`, which is salted per process. The pool must be an ordered, versioned list, because reordering it remaps everyone.
3. **Persist** the first assignment to `voices.json` (`user_id -> {voice, instructions?}`). From then on, the file is the source of truth, so adding voices to the pool later does not remap existing people.
4. **User overrides** live in the same file or config and always win.
5. **Session de-dup**: collisions are likely. With 5 authors in an episode, the chance of a clash is 58% from 13 voices, 31% from 28, and 30% from 30 (birthday bound). Before rendering an episode, check the authors present. If two share a voice, the later author (by first appearance) gets the next free voice from its hash slot for this episode only. The persisted mapping is not changed.
6. **Kokoro blending** can create extra stable voices: hash to a pair `(a, b)` and use `"a,b"`. Blends of similar voices may sound alike, so curate the pool by ear.
7. **Gender/accent hints**: optional. Keep the pool split by tag only if users request it. This is not needed for the MVP.

## C. Data privacy / retention (cloud)

| Provider | Trains on API data by default? | Default retention | Zero-retention option |
|---|---|---|---|
| OpenAI | No [35] | `/v1/audio/speech`: abuse-monitoring logs kept **30 days** [35] | ZDR applies to this endpoint, but needs prior approval via sales. Modified Abuse Monitoring also needs approval [35] |
| ElevenLabs | **Yes, unless you opt out**: the Terms let users opt out of training via account "Data use" settings [36]. The Privacy Policy says personal data may be used to train models [37] | History saved by default. API delete removes it immediately; backups last up to 30 days; debug/moderation logs may keep data [38] | Zero Retention Mode (`enable_logging=false`) is for **select Enterprise customers only**. It covers TTS and Text to Dialogue, API only [38] |
| Google Cloud TTS | No: "won't use your data to train ... without your prior permission" [39] | "Google does not log any customer Cloud TTS text or audio data" [40]. Gemini models generally cache in-memory for 24 h (can be disabled per project), and abuse-monitoring logging may apply with an exception on request [39]. Whether this applies to Gemini-TTS through the Cloud TTS API is **unverified** | Disable the cache and request an abuse-monitoring exception [39] |
| Azure Speech | Not stated on the TTS privacy page (unverified; covered by the Microsoft DPA) | Prebuilt voices: "Neither input text nor output audio content is stored in Microsoft logs" [41]. Batch synthesis keeps job history 168 h by default, up to 744 h; delete it after download [42] | Real-time API is already no-log [41] |

## Recommendation (MVP)

Default to **local Kokoro**, behind a `TTSBackend` interface, and offer **OpenAI `gpt-4o-mini-tts`** as the optional cloud "expressive" backend. Workplace Slack content then never leaves the laptop, which avoids vendor and DPA questions. Marginal cost is $0, episodes render before the commute so no connectivity is needed, licensing is Apache throughout, and 28 voices plus blending cover distinct-per-author. The trade-off is flat emotion. OpenAI is the cheapest expressive upgrade (~$0.91/h, unverified), with no training by default and 30-day logs. ElevenLabs v4 with Text to Dialogue sounds most like radio, but it costs 2-5x more and trains on content unless you opt out.

## Sources
[1] https://elevenlabs.io/docs/overview/capabilities/text-to-speech
[2] https://elevenlabs.io/docs/models
[3] https://elevenlabs.io/pricing/api
[4] https://elevenlabs.io/docs/capabilities/text-to-dialogue
[5] https://developers.openai.com/api/docs/guides/text-to-speech
[6] https://developers.openai.com/api/docs/models/gpt-4o-mini-tts
[7] https://developers.openai.com/api/docs/pricing
[8] https://cloud.google.com/text-to-speech/docs/chirp3-hd
[9] https://cloud.google.com/text-to-speech/pricing
[10] https://cloud.google.com/text-to-speech/docs/gemini-tts
[11] https://ai.google.dev/gemini-api/docs/speech-generation
[12] https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
[13] https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice
[14] https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/
[15] https://prices.azure.com/api/retail/prices (Azure Retail Prices API, eastus, meters "S1 Neural Text To Speech Characters" $15/1M, "Neural HD Text to Speech Characters" $22/1M)
[16] https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices
[17] https://huggingface.co/hexgrad/Kokoro-82M
[18] https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
[19] https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py (`load_voice`)
[20] https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX
[21] https://github.com/hexgrad/kokoro
[22] https://github.com/OHF-Voice/piper1-gpl
[23] https://github.com/rhasspy/piper
[24] https://huggingface.co/rhasspy/piper-voices/tree/main/en
[25] https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/libritts_r/medium/MODEL_CARD
[26] https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md
[27] https://github.com/kyutai-labs/pocket-tts
[28] https://huggingface.co/kyutai/pocket-tts, https://huggingface.co/kyutai/tts-1.6b-en_fr
[29] https://huggingface.co/kyutai/tts-voices
[30] https://github.com/resemble-ai/chatterbox
[31] https://huggingface.co/ResembleAI/chatterbox
[32] https://github.com/nari-labs/dia
[33] https://huggingface.co/nari-labs/Dia-1.6B
[34] https://github.com/microsoft/VibeVoice
[35] https://developers.openai.com/api/docs/guides/your-data
[36] https://elevenlabs.io/terms-of-use (section "Data Deletion and Opt Out")
[37] https://elevenlabs.io/privacy-policy
[38] https://elevenlabs.io/docs/resources/zero-retention-mode
[39] https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention
[40] https://cloud.google.com/text-to-speech/docs/data-logging
[41] https://learn.microsoft.com/en-us/legal/cognitive-services/speech-service/text-to-speech/data-privacy-security
[42] https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-synthesis
