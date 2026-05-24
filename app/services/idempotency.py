"""msg_id 幂等去重（一期：内存 LRU）。"""
from collections import OrderedDict
import threading

_MAX = 2000
_seen: "OrderedDict[str, int]" = OrderedDict()
_lock = threading.Lock()


def seen_or_record(msg_id: str) -> bool:
    """如果之前见过返回 True；否则记录并返回 False。"""
    if not msg_id:
        return False
    with _lock:
        if msg_id in _seen:
            _seen.move_to_end(msg_id)
            return True
        _seen[msg_id] = 1
        if len(_seen) > _MAX:
            _seen.popitem(last=False)
        return False
