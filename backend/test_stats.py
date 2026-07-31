import tempfile
import unittest
from pathlib import Path

from main import (
    _get_listened_count,
    _record_listen,
)


class ListeningStatsTest(unittest.TestCase):
    def test_recordings_are_unique_per_case_sensitive_username(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "stats.sqlite3"

            self.assertEqual(_record_listen("audio.m4a", "Alice", database), 1)
            self.assertEqual(_record_listen("audio.m4a", "Alice", database), 1)
            self.assertEqual(_record_listen("another.m4a", "Alice", database), 2)
            self.assertEqual(_record_listen("audio.m4a", "alice", database), 1)
            self.assertEqual(_get_listened_count("Alice", database), 2)
            self.assertEqual(_get_listened_count("alice", database), 1)


if __name__ == "__main__":
    unittest.main()
