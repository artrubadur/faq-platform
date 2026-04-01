import zlib
from collections import OrderedDict
from typing import Any


class DuplicateFilter:
    def __init__(self, cached_limit: int, repeat_limit: int):
        self.cached_limit = cached_limit
        self.repeat_limit = repeat_limit
        self._history: OrderedDict[int, int] = OrderedDict()

    def _create_cache_key(self, record: dict[str, Any]) -> int:
        raw_key = (record["level"].name, record["message"], record["extra"])
        return zlib.adler32(str(raw_key).encode())

    def __call__(self, record: dict[str, Any]):
        key = self._create_cache_key(record)
        count = self._history[key]  #  Executed after the patch
        return count <= self.repeat_limit

    def _increment_history(self, key: int):
        if key in self._history:
            self._history.move_to_end(key)

        count = self._history.get(key, 0) + 1
        self._history[key] = count

        if len(self._history) > self.cached_limit:
            self._history.popitem(last=False)

        return count

    def get_count(self, record) -> int:
        key = self._create_cache_key(record)
        return self._increment_history(key)


def make_duplicate_patch(duplicate_filter: DuplicateFilter, repeat_limit: int):
    def duplicate_patch(record):
        count = duplicate_filter.get_count(record)
        if count > 1 and count <= repeat_limit:
            record["_repeat"] = count

    return duplicate_patch
