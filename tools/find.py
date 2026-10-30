"""Compatibility wrapper — the implementation lives in the installed
skill (skills/hoi4-modding/scripts/)."""

import importlib.util
import sys
from pathlib import Path

_impl = Path(__file__).resolve().parents[1] / "skills" / "hoi4-modding" / "scripts" / "find.py"
_spec = importlib.util.spec_from_file_location("_hoi4_dev_skills_find", _impl)
_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod  # dataclass introspection needs it registered
_spec.loader.exec_module(_mod)
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("__")})

# direct handle to the implementation module (for monkeypatching)
_impl_module = _mod
