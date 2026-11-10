from __future__ import annotations

import re
from pathlib import Path

from .schemas import Beat, Episode

TIME = re.compile(r"(\d{2}):(\d{2})\.(\d{2})")
EPISODE = re.compile(r"EPISODE NUMBER:\s*Episode\s*(\d+)", re.I)
SCENE = re.compile(r"SCENE\s+(\d+)")
FIELD = re.compile(
    r"\*\*(?P<label>[^*]+):\*\*\s*\nStart:\s*\((?P<start>[^)]+)\)\s*\|\s*End:\s*\((?P<end>[^)]+)\)\s*\n(?P<text>.*?)(?=\n\*\*[^*]+:\*\*\s*\nStart:|\nSCENE\s+\d+|\n--- SCRIPT END ---|\Z)",
    re.S,
)


def to_seconds(value: str) -> float:
    match = TIME.search(value.strip())
    if not match:
        raise ValueError(f"Invalid timestamp: {value}")
    minute, second, centisecond = (int(part) for part in match.groups())
    return minute * 60 + second + centisecond / 100


def format_time(seconds: float) -> str:
    minutes, seconds = divmod(max(0, seconds), 60)
    whole = int(seconds)
    hundredths = round((seconds - whole) * 100)
    return f"{int(minutes):02}:{whole % 60:02}.{hundredths:02}"


def _clean(value: str) -> str:
    # Dataset text can arrive as UTF-8 decoded through a Windows code page.
    value = value.strip().replace("â€“", "–").replace("â€™", "’").replace("Ã©", "é")
    return re.sub(r"\s+", " ", value)


def parse_text(raw: str, source_file: str = "uploaded-script.txt") -> Episode:
    episode_match = EPISODE.search(raw)
    if not episode_match:
        raise ValueError(f"Could not find episode number in {source_file}")
    logline = re.search(r"EPISODE LOGLINE:\s*(.+)", raw)
    continuity = re.search(r"CONTINUITY NOTES:\s*(.+)", raw)
    episode = Episode(int(episode_match.group(1)), _clean(logline.group(1)) if logline else "", _clean(continuity.group(1)) if continuity else "", source_file)
    scene = 0
    for chunk in re.split(r"(?=\nSCENE\s+\d+)", raw):
        scene_match = SCENE.search(chunk)
        if scene_match:
            scene = int(scene_match.group(1))
        for match in FIELD.finditer(chunk):
            label, text = _clean(match.group("label")), _clean(match.group("text"))
            if label.startswith("CAMERA") or not text:
                continue
            kind = "action" if label.startswith(("ACTION", "SOUND FX")) else "dialogue"
            speaker = None if kind == "action" else label.split("(")[0].strip()
            try:
                start, end = to_seconds(match.group("start")), to_seconds(match.group("end"))
            except ValueError:
                continue
            if end > start:
                episode.beats.append(Beat(episode.number, scene, kind, start, end, text, speaker))
    episode.beats.sort(key=lambda beat: (beat.start, beat.end))
    return episode


def parse_episode(path: str | Path) -> Episode:
    path = Path(path)
    return parse_text(path.read_text(encoding="utf-8", errors="replace"), path.name)


def parse_directory(directory: str | Path) -> list[Episode]:
    return [parse_episode(path) for path in sorted(Path(directory).rglob("*.txt"))]
