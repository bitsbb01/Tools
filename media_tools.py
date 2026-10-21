"""Command construction and validation for JGJG Video Studio."""

from __future__ import annotations

import re
from pathlib import Path


RESOLUTIONS = {
    "Original": None,
    "720p (1280 × 720)": (1280, 720),
    "1080p (1920 × 1080)": (1920, 1080),
    "Square (1080 × 1080)": (1080, 1080),
    "Vertical (1080 × 1920)": (1080, 1920),
}


def parse_time(value: str) -> float:
    """Parse seconds or HH:MM:SS[.sss] into seconds."""
    value = value.strip()
    if not value:
        raise ValueError("Enter a time value.")
    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        result = float(value)
    else:
        parts = value.split(":")
        if len(parts) not in (2, 3):
            raise ValueError("Use seconds or HH:MM:SS format.")
        try:
            nums = [float(x) for x in parts]
        except ValueError as exc:
            raise ValueError("Time must contain numbers only.") from exc
        if any(x < 0 for x in nums) or (len(nums) == 3 and nums[1] >= 60) or nums[-1] >= 60:
            raise ValueError("Minutes and seconds must be under 60, and time cannot be negative.")
        result = nums[0] * 60 + nums[1] if len(nums) == 2 else nums[0] * 3600 + nums[1] * 60 + nums[2]
    if result < 0:
        raise ValueError("Time cannot be negative.")
    return result


def build_ffmpeg_command(
    ffmpeg: str,
    source: str,
    output: str,
    start: float,
    duration: float,
    resolution: str = "Original",
    music: str | None = None,
) -> list[str]:
    """Build a safe argument-list (never shell-interpolated) FFmpeg command."""
    if duration <= 0:
        raise ValueError("Clip length must be greater than zero.")
    if not Path(source).is_file():
        raise ValueError("Choose an existing video file.")
    if music and not Path(music).is_file():
        raise ValueError("The selected music file does not exist.")
    if resolution not in RESOLUTIONS:
        raise ValueError("Choose one of the listed output sizes.")

    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", source]
    if music:
        command += ["-stream_loop", "-1", "-i", music]
    command += ["-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-map", "0:v:0"]
    if music:
        command += ["-map", "1:a:0"]
    else:
        command += ["-map", "0:a?"]

    dimensions = RESOLUTIONS[resolution]
    if dimensions:
        width, height = dimensions
        command += ["-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"]
    command += ["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-progress", "pipe:1", "-nostats", output]
    return command
