# Ensure the workspace root is first on sys.path so that `shared.*` resolves to
# the top-level shared/ package, not agents/shared/ (which has no tools/ subpackage).
# This must run before any relative imports so the fix is in place before agent.py.
import pathlib as _p
import sys as _s

_root = str(_p.Path(__file__).resolve().parent.parent.parent)
if not _s.path or _s.path[0] != _root:
    if _root in _s.path:
        _s.path.remove(_root)
    _s.path.insert(0, _root)

# If a previous import already cached agents/shared/ as `shared`, evict it.
_cached_shared = _s.modules.get("shared")
if _cached_shared is not None and not hasattr(_cached_shared, "tools"):
    for _k in [k for k in _s.modules if k == "shared" or k.startswith("shared.")]:
        del _s.modules[_k]

del _p, _s, _root

from .agent import root_agent
from .app import app

__all__ = ["root_agent", "app"]
