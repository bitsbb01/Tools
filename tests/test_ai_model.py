import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_model import INSTALLED_MARKER, MODEL_REPO, _model_files, model_is_installed


class ModelRepositoryTests(unittest.TestCase):
    def test_file_listing_keeps_model_and_tokenizer_but_skips_demo_assets(self):
        payload = [
            {"type": "file", "path": "config.json", "size": 42},
            {"type": "file", "path": "diffusion.safetensors", "size": 100},
            {"type": "file", "path": "google/umt5/tokenizer.json", "size": 20},
            {"type": "file", "path": "assets/demo.png", "size": 90},
            {"type": "file", "path": "examples/input.jpg", "size": 90},
            {"type": "file", "path": "../outside.txt", "size": 1},
            {"type": "file", "path": ".gitattributes", "size": 1},
        ]
        with patch("ai_model._request_json", return_value=(payload, None)):
            files = _model_files()
        self.assertEqual(
            [item["path"] for item in files],
            ["config.json", "diffusion.safetensors", "google/umt5/tokenizer.json"],
        )

    def test_installed_marker_must_match_model_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.assertFalse(model_is_installed(root))
            (root / INSTALLED_MARKER).write_text(json.dumps({"repository": "wrong/model", "complete": True}))
            self.assertFalse(model_is_installed(root))
            (root / "config.json").write_text("{}")
            (root / INSTALLED_MARKER).write_text(json.dumps({
                "repository": MODEL_REPO,
                "complete": True,
                "files": [{"path": "config.json", "size": 2}],
            }))
            self.assertTrue(model_is_installed(root))
            (root / "config.json").write_text("broken")
            self.assertFalse(model_is_installed(root))


if __name__ == "__main__":
    unittest.main()
