from __future__ import annotations

import sys
import time
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "expected"))
from generated_ttl_cache import TTLCache


class TTLCacheAcceptanceTests(unittest.TestCase):
    def test_generic_type_parameters_and_basic_stats(self):
        cache = TTLCache[int, str](max_size=2, default_ttl=1.0)
        cache.set(1, "one")
        self.assertEqual(cache.get(1), "one")
        self.assertEqual(cache.get(99, "missing"), "missing")
        self.assertEqual(cache.stats["hits"], 1)
        self.assertEqual(cache.stats["misses"], 1)

    def test_invalid_constructor_arguments(self):
        with self.assertRaises(ValueError): TTLCache(max_size=0)
        with self.assertRaises(ValueError): TTLCache(default_ttl=0)
        with self.assertRaises(ValueError): TTLCache(default_ttl=-1)

    def test_lru_eviction(self):
        cache = TTLCache[str, int](max_size=2)
        cache.set("a", 1); cache.set("b", 2)
        self.assertEqual(cache.get("a"), 1)
        cache.set("c", 3)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("c"), 3)
        self.assertEqual(cache.stats["evictions"], 1)

    def test_per_entry_and_default_ttl(self):
        cache = TTLCache[str, int](max_size=4, default_ttl=0.04)
        cache.set("short", 1, ttl=0.01); cache.set("default", 2)
        time.sleep(0.025)
        self.assertIsNone(cache.get("short")); self.assertEqual(cache.get("default"), 2)
        time.sleep(0.03)
        self.assertIsNone(cache.get("default"))
        self.assertGreaterEqual(cache.stats["expirations"], 2)

    def test_delete_and_clear(self):
        cache = TTLCache[str, int](max_size=4)
        cache.set("a", 1); cache.set("b", 2); cache.delete("a")
        self.assertIsNone(cache.get("a")); cache.clear()
        self.assertIsNone(cache.get("b"))

    def test_thread_safety_under_concurrent_access(self):
        cache = TTLCache[int, int](max_size=64, default_ttl=5.0)
        failures: list[BaseException] = []; lock = threading.Lock()
        def worker(offset: int) -> None:
            try:
                for i in range(100):
                    key = offset * 1000 + i; cache.set(key, i); cache.get(key)
            except BaseException as exc:
                with lock: failures.append(exc)
        with ThreadPoolExecutor(max_workers=8) as pool: list(pool.map(worker, range(8)))
        self.assertFalse(failures, failures); self.assertGreater(cache.stats["hits"], 0)
