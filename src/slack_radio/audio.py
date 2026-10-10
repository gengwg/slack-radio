import asyncio
import re
import subprocess
import tempfile
from pathlib import Path

import edge_tts

from slack_radio.speech import Chapter

RATE = 24000
LINE_GAP = 0.35
CHAPTER_GAP = 1.0
CONCURRENCY = 4


async def _synthesize(jobs: list[tuple[str, str, Path]]) -> None:
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(text: str, voice: str, path: Path) -> None:
        async with sem:
            await edge_tts.Communicate(text, voice).save(str(path))

    await asyncio.gather(*(one(*job) for job in jobs))


def _pcm(path: Path) -> bytes:
    return subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "s16le",
            "-ac",
            "1",
            "-ar",
            str(RATE),
            "-",
        ],
        check=True,
        capture_output=True,
    ).stdout


def _silence(seconds: float) -> bytes:
    return bytes(2 * int(RATE * seconds))


def _escape(value: str) -> str:
    # ffmetadata treats =, ;, #, backslash and newline as special.
    return re.sub(r"([=;#\\\n])", r"\\\1", value)


def _ms(nbytes: int) -> int:
    return nbytes * 1000 // (2 * RATE)


def assemble(chapters: list[tuple[str, list[Path]]], out: Path, title: str) -> float:
    """Join audio segments into one MP3 with an ID3 chapter per entry. Returns seconds."""
    pcm = bytearray()
    marks = []
    for name, segments in chapters:
        start = len(pcm)
        for seg in segments:
            pcm += _pcm(seg) + _silence(LINE_GAP)
        pcm += _silence(CHAPTER_GAP)
        marks.append((name, start, len(pcm)))

    meta = [";FFMETADATA1", f"title={_escape(title)}"]
    for name, start, end in marks:
        meta += [
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            f"START={_ms(start)}",
            f"END={_ms(end)}",
            f"title={_escape(name)}",
        ]
    with tempfile.TemporaryDirectory() as tmp:
        meta_path = Path(tmp, "meta.txt")
        meta_path.write_text("\n".join(meta) + "\n")
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(RATE), "-ac", "1",
             "-i", "-", "-i", str(meta_path), "-map", "0:a", "-map_metadata", "1",
             "-map_chapters", "1", "-c:a", "libmp3lame", "-b:a", "64k",
             "-id3v2_version", "3", str(out)],
            input=bytes(pcm),
            check=True,
        )  # fmt: skip
    return len(pcm) / (2 * RATE)


def render(
    chapters: list[Chapter], voices: dict[str | None, str], out: Path, title: str
) -> float:
    """Synthesize every line with its speaker's voice and write one MP3."""
    with tempfile.TemporaryDirectory() as tmp:
        jobs, layout = [], []
        for c in chapters:
            paths = []
            for line in c.lines:
                path = Path(tmp, f"{len(jobs):05}.mp3")
                jobs.append((line.text, voices[line.speaker], path))
                paths.append(path)
            layout.append((c.title, paths))
        asyncio.run(_synthesize(jobs))
        return assemble(layout, out, title)
