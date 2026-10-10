import hashlib
import json
from pathlib import Path

NARRATOR_VOICE = "en-US-AndrewNeural"

# Order matters: default assignments hash into this list. Append only.
POOL = [
    "en-US-AvaNeural",
    "en-US-BrianNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "en-US-EmmaNeural",
    "en-US-GuyNeural",
    "en-AU-NatashaNeural",
    "en-IE-ConnorNeural",
    "en-US-JennyNeural",
    "en-US-EricNeural",
    "en-GB-LibbyNeural",
    "en-GB-ThomasNeural",
    "en-IE-EmilyNeural",
    "en-CA-LiamNeural",
    "en-US-AriaNeural",
    "en-US-RogerNeural",
    "en-CA-ClaraNeural",
    "en-NZ-MitchellNeural",
    "en-US-MichelleNeural",
    "en-US-SteffanNeural",
    "en-NZ-MollyNeural",
    "en-ZA-LukeNeural",
    "en-ZA-LeahNeural",
    "en-AU-WilliamMultilingualNeural",
    "en-IN-NeerjaExpressiveNeural",
    "en-IN-PrabhatNeural",
    "en-GB-MaisieNeural",
]


def default_voice(team_id: str, user_id: str) -> str:
    digest = hashlib.sha256(f"{team_id}:{user_id}".encode()).digest()
    return POOL[int.from_bytes(digest[:8]) % len(POOL)]


def assign(path: Path, team_id: str, speakers: dict[str, str]) -> dict[str, str]:
    """Map speaker IDs (in order of appearance) to voices for one episode.

    speakers maps Slack IDs to display names. Persisted choices in `path` win and
    can be edited by hand. Two speakers sharing a voice in the same episode get
    a temporary next free voice; the saved mapping is unchanged.
    """
    saved = json.loads(path.read_text()) if path.exists() else {}
    for uid, name in speakers.items():
        saved.setdefault(uid, {"name": name, "voice": default_voice(team_id, uid)})
    path.write_text(json.dumps(saved, indent=2) + "\n")

    episode: dict[str, str] = {}
    used: set[str] = set()
    for uid in speakers:
        voice = saved[uid]["voice"]
        if voice in used and voice in POOL:
            start = POOL.index(voice)
            free = [POOL[(start + i) % len(POOL)] for i in range(1, len(POOL))]
            voice = next((v for v in free if v not in used), voice)
        episode[uid] = voice
        used.add(voice)
    return episode
