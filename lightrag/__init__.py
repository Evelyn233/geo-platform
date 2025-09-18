"""
Compatibility shim for LightRAG imports.

This local package named `lightrag` forwards to the actually installed
distribution which may use a different project name (e.g. `lightrag_hku`).
It exposes `LightRAG`, `QueryParam`, and re-exports common submodules
so existing imports like `from lightrag.utils import EmbeddingFunc` work.
"""

import importlib
import sys
import pkgutil
from types import ModuleType


def _import_first(*candidates: str) -> ModuleType:
    last_err = None
    for name in candidates:
        try:
            return importlib.import_module(name)
        except Exception as e:
            last_err = e
            continue
    raise last_err or ImportError("No LightRAG backend module found")


# Try various possible import names for LightRAG
_backend = _import_first("lightrag_hku", "lightrag_hku.lightrag", "lightrag_hku.LightRAG", "lightrag_hku.core", "lightrag_hku.api")


def _maybe_register_submodule(alias: str, target: str) -> None:
    try:
        mod = importlib.import_module(target)
        sys.modules[alias] = mod
    except Exception:
        pass


# Expose common submodules under the `lightrag.*` namespace
_maybe_register_submodule("lightrag.utils", f"{_backend.__name__}.utils")
_maybe_register_submodule("lightrag.operate", f"{_backend.__name__}.operate")
_maybe_register_submodule("lightrag.kg.shared_storage", f"{_backend.__name__}.kg.shared_storage")


def _find_symbol(symbol: str):
    # Try top-level, then common internal modules
    for mod_name in (
        _backend.__name__,
        f"{_backend.__name__}.core",
        f"{_backend.__name__}.lightrag",
        f"{_backend.__name__}.api",
    ):
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, symbol):
                return getattr(mod, symbol)
        except Exception:
            continue
    return None


# Public symbols commonly used by RAG-Anything
LightRAG = _find_symbol("LightRAG")
QueryParam = _find_symbol("QueryParam")

# If not found directly, scan subpackages to locate the class dynamically
if LightRAG is None:
    prefix = _backend.__name__ + "."
    for modinfo in pkgutil.walk_packages(_backend.__path__, prefix=prefix):
        name = modinfo.name
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "LightRAG"):
                LightRAG = getattr(mod, "LightRAG")
                # opportunistically expose QueryParam if present
                if hasattr(mod, "QueryParam") and QueryParam is None:
                    QueryParam = getattr(mod, "QueryParam")
                break
        except Exception:
            continue

if LightRAG is None:
    raise ImportError("Could not locate LightRAG class in installed backend package")


__all__ = ["LightRAG", "QueryParam"]


