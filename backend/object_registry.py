"""Simple in-memory registry to preserve wrapper identity by db id.

This helps the test suite which expects the same Python wrapper objects
to be returned after DB-backed loading.
"""
_REGISTRY = {}

def register(kind: str, db_id: int, obj):
    if db_id is None:
        return
    _REGISTRY.setdefault(kind, {})[int(db_id)] = obj

def get(kind: str, db_id: int):
    if db_id is None:
        return None
    return _REGISTRY.get(kind, {}).get(int(db_id))

def unregister(kind: str, db_id: int):
    if db_id is None:
        return
    kind_map = _REGISTRY.get(kind)
    if kind_map and int(db_id) in kind_map:
        del kind_map[int(db_id)]
