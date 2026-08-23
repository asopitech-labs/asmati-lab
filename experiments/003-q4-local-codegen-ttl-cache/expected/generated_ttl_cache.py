from typing import Generic, TypeVar, Optional
from collections import OrderedDict
import threading
import time

K = TypeVar('K')
V = TypeVar('V')


class TTLCache(Generic[K, V]):
    def __init__(self, max_size: int = 128, default_ttl: Optional[float] = None):
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        if default_ttl is not None and default_ttl <= 0:
            raise ValueError("default_ttl must be > 0 if provided")
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._data: OrderedDict[K, tuple[V, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._expirations = 0

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        with self._lock:
            effective_ttl = ttl if ttl is not None else self._default_ttl
            if effective_ttl is not None and effective_ttl <= 0:
                raise ValueError("ttl must be > 0 if provided")
            expires_at = time.monotonic() + effective_ttl if effective_ttl is not None else float('inf')
            if key in self._data:
                self._data[key] = (value, expires_at)
                self._data.move_to_end(key)
            else:
                self._data[key] = (value, expires_at)
                self._data.move_to_end(key)
                while len(self._data) > self._max_size:
                    self._data.popitem(last=False)
                    self._evictions += 1

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            if key not in self._data:
                self._misses += 1
                return default
            value, expires_at = self._data[key]
            if time.monotonic() >= expires_at:
                del self._data[key]
                self._expirations += 1
                self._misses += 1
                return default
            self._data.move_to_end(key)
            self._hits += 1
            return value

    def delete(self, key: K) -> None:
        with self._lock:
            if key in self._data:
                del self._data[key]

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    @property
    def stats(self) -> dict:
        with self._lock:
            return {
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "expirations": self._expirations,
                "size": len(self._data),
                "max_size": self._max_size,
            }
