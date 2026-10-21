import tempfile
import unittest
from pathlib import Path

from media_tools import build_ffmpeg_command, parse_time


class ParseTimeTests(unittest.TestCase):
    def test_accepts_seconds_and_clock_formats(self):
        self.assertEqual(parse_time("12.5"), 12.5)
        self.assertEqual(parse_time("02:03"), 123)
        self.assertEqual(parse_time("01:02:03.5"), 3723.5)

    def test_rejects_invalid_clock(self):
        with self.assertRaises(ValueError):
            parse_time("00:65:00")


class CommandTests(unittest.TestCase):
    def test_creates_trim_resize_command_without_shell_string(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "my clip.mp4"
            source.touch()
            command = build_ffmpeg_command("ffmpeg", str(source), str(Path(folder) / "out.mp4"), 2, 5, "720p (1280 × 720)")
            self.assertIn("-ss", command)
            self.assertIn("-t", command)
            self.assertIn("libx264", command)
            self.assertTrue(any("1280:720" in item for item in command))
            self.assertIn(str(source), command)

    def test_maps_replacement_music_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.mp4"
            music = Path(folder) / "music.mp3"
            source.touch()
            music.touch()
            command = build_ffmpeg_command("ffmpeg", str(source), str(Path(folder) / "out.mp4"), 0, 8, music=str(music))
            self.assertIn("1:a:0", command)
            self.assertIn("-stream_loop", command)


if __name__ == "__main__":
    unittest.main()
