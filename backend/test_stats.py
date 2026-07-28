import tempfile
import unittest
from pathlib import Path

from main import (
    _get_play_count,
    _increment_play_count,
    _list_recordings,
    _save_recording,
)


class PlayCountTest(unittest.TestCase):
    def test_play_count_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "stats.sqlite3"

            self.assertEqual(_get_play_count("audio.m4a", database), 0)
            self.assertEqual(_increment_play_count("audio.m4a", database), 1)
            self.assertEqual(_increment_play_count("audio.m4a", database), 2)
            self.assertEqual(_get_play_count("audio.m4a", database), 2)

            _save_recording("audio.m4a", "小明", database)
            self.assertEqual(
                _list_recordings("小明", database),
                [
                    {
                        "filename": "audio.m4a",
                        "url": "/api/audio/audio.m4a",
                        "created_at": _list_recordings("小明", database)[0]["created_at"],
                        "play_count": 2,
                    }
                ],
            )
            self.assertEqual(_list_recordings("其他人", database), [])


if __name__ == "__main__":
    unittest.main()
