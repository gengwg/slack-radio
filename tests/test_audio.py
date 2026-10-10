import json
import subprocess

from slack_radio import audio
from slack_radio.speech import NARRATOR, Chapter, Line


def probe(path):
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_chapters",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
    ).stdout
    return json.loads(out)


def tone(path, seconds):
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"sine=duration={seconds}",
            str(path),
        ],
        check=True,
    )
    return path


def test_assemble_writes_chapters(tmp_path):
    a, b = tone(tmp_path / "a.mp3", 1), tone(tmp_path / "b.mp3", 2)
    out = tmp_path / "ep.mp3"
    seconds = audio.assemble([("Intro", [a]), ("#deploys = ops", [a, b])], out, "Ep")
    info = probe(out)
    chapters = [(c["tags"]["title"], float(c["start_time"])) for c in info["chapters"]]
    assert chapters == [("Intro", 0.0), ("#deploys = ops", 2.35)]
    assert abs(float(info["format"]["duration"]) - seconds) < 0.2


def test_render_with_real_tts(tmp_path):
    """Hits the network: Microsoft Edge TTS."""
    chapters = [Chapter("Intro", [Line(NARRATOR, "Hello."), Line("U1", "Hi there.")])]
    cast = {NARRATOR: "en-US-AndrewNeural", "U1": "en-GB-SoniaNeural"}
    out = tmp_path / "ep.mp3"
    seconds = audio.render(chapters, cast, out, "Test")
    assert 1 < seconds < 10
    assert probe(out)["chapters"][0]["tags"]["title"] == "Intro"
