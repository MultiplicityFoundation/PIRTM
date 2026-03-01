#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
INIT = ROOT / "src" / "pirtm" / "__init__.py"
CHANGELOG = ROOT / "CHANGELOG.md"

SEMVER_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:([a-z]+)(\d+))?$")


def parse_version(value: str) -> tuple[int, int, int, str | None, int | None]:
    match = SEMVER_PATTERN.match(value)
    if not match:
        raise ValueError(f"invalid version: {value}")
    major, minor, patch, prerelease, prerelease_num = match.groups()
    return (
        int(major),
        int(minor),
        int(patch),
        prerelease,
        int(prerelease_num) if prerelease_num is not None else None,
    )


def format_version(parts: tuple[int, int, int, str | None, int | None]) -> str:
    major, minor, patch, prerelease, prerelease_num = parts
    base = f"{major}.{minor}.{patch}"
    if prerelease is None:
        return base
    if prerelease_num is None:
        return f"{base}{prerelease}"
    return f"{base}{prerelease}{prerelease_num}"


def load_current_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("version not found in pyproject.toml")
    return match.group(1)


def bump(base: str, level: str, prerelease: str | None) -> str:
    major, minor, patch, current_pre, _ = parse_version(base)

    if level == "release":
        if current_pre is None:
            raise ValueError("current version is already stable; use major/minor/patch")
        return format_version((major, minor, patch, None, None))

    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "patch":
        patch += 1
    else:
        raise ValueError(f"unsupported level: {level}")

    if prerelease:
        return format_version((major, minor, patch, prerelease, 1))
    return format_version((major, minor, patch, None, None))


def replace_version(path: Path, current: str, target: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(current, target)
    if updated == text:
        raise RuntimeError(f"version {current} not found in {path}")
    path.write_text(updated, encoding="utf-8")


def update_changelog(version: str) -> None:
    if not CHANGELOG.exists():
        return
    text = CHANGELOG.read_text(encoding="utf-8")
    marker = "## [Unreleased]"
    release_header = f"## [{version}]"
    if marker in text and release_header not in text:
        text = text.replace(marker, marker + "\n\n### Added\n- \n\n" + release_header, 1)
        CHANGELOG.write_text(text, encoding="utf-8")


def finalize_release_date(version: str) -> None:
    if not CHANGELOG.exists():
        return
    text = CHANGELOG.read_text(encoding="utf-8")
    text = text.replace(f"## [{version}] - YYYY-MM-DD", f"## [{version}] - {date.today().isoformat()}")
    CHANGELOG.write_text(text, encoding="utf-8")


def git_tag(version: str) -> None:
    subprocess.run(["git", "tag", f"v{version}"], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump package version across project files.")
    parser.add_argument(
        "level",
        choices=["major", "minor", "patch", "release"],
        help="SemVer operation to apply",
    )
    parser.add_argument("--pre", choices=["a", "b", "rc"], default=None, help="Prerelease marker")
    parser.add_argument("--tag", action="store_true", help="Create git tag v<version>")
    args = parser.parse_args()

    if args.level == "release" and args.pre is not None:
        raise ValueError("--pre cannot be used with release level")

    current = load_current_version()
    target = bump(current, args.level, args.pre)

    replace_version(PYPROJECT, current, target)
    replace_version(INIT, current, target)
    update_changelog(target)
    if args.level == "release":
        finalize_release_date(target)

    if args.tag:
        git_tag(target)

    print(f"bumped version: {current} -> {target}")


if __name__ == "__main__":
    main()
