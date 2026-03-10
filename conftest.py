"""
Root pytest configuration for PIRTM test suite.

Ensures the pirtm package is importable during test discovery even when
the package has not been installed via pip (e.g., in a bare checkout).
"""
import sys
import os

# Add the parent directory to sys.path so `import pirtm` resolves to
# the package at /path/to/PIRTM (the directory containing this conftest).
_pkg_parent = os.path.dirname(os.path.abspath(__file__))

# Only add the symlink-based workaround when the package is NOT already
# installed (i.e., `import pirtm` would fail).
try:
    import pirtm  # noqa: F401
except ModuleNotFoundError:
    # The repo directory is named PIRTM (uppercase) but the package must be
    # importable as `pirtm` (lowercase).  Create a temporary in-process
    # mapping by inserting a finder that redirects `pirtm` → the repo root.
    import importlib
    import types  # noqa: F401

    class _PirtmFinder:
        """Meta path finder that maps `pirtm` to the repo root package."""

        def find_spec(self, name, path, target=None):
            if name == "pirtm" or name.startswith("pirtm."):
                rel = name[len("pirtm"):]  # e.g. "" or ".core.recurrence"
                parts = rel.lstrip(".").split(".") if rel else []
                pkg_path = os.path.join(_pkg_parent, *parts)
                init = os.path.join(pkg_path, "__init__.py")
                if os.path.isfile(init) or (not parts and os.path.isfile(
                        os.path.join(_pkg_parent, "__init__.py"))):
                    return importlib.util.spec_from_file_location(
                        name,
                        os.path.join(_pkg_parent if not parts else pkg_path,
                                     "__init__.py"),
                        submodule_search_locations=[
                            _pkg_parent if not parts else pkg_path
                        ],
                    )
            return None

    sys.meta_path.insert(0, _PirtmFinder())
