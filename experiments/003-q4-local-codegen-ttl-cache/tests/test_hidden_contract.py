from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "expected"))
from generated_ttl_cache import TTLCache


class TTLCacheAdditionalTests(unittest.TestCase):
    def test_clear_preserves_cumulative_statistics(self):
        cache = TTLCache[str, int](max_size=2)
        cache.set("a", 1); self.assertEqual(cache.get("a"), 1)
        self.assertIsNone(cache.get("missing")); cache.clear()
        self.assertEqual(cache.stats["hits"], 1)
        self.assertEqual(cache.stats["misses"], 1)
        self.assertEqual(cache.stats["size"], 0)

    def test_replacing_key_is_not_an_eviction(self):
        cache = TTLCache[str, int](max_size=1)
        cache.set("a", 1); cache.set("a", 2)
        self.assertEqual(cache.get("a"), 2)
        self.assertEqual(cache.stats["evictions"], 0)
        self.assertEqual(cache.stats["size"], 1)

    def test_expiration_is_counted_once(self):
        cache = TTLCache[str, int](max_size=2)
        cache.set("short", 1, ttl=0.01); time.sleep(0.03)
        self.assertIsNone(cache.get("short")); self.assertIsNone(cache.get("short"))
        self.assertEqual(cache.stats["expirations"], 1)
        self.assertEqual(cache.stats["misses"], 2)
