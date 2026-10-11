#!/usr/bin/env python3
"""Reassemble the four original showcase documents after validating every file."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile


TRANSFER_DIR = PurePosixPath(".github/showcase-transfer")
ALLOWED_TARGETS = frozenset({
    "examples/progress-report/Robot-Assembly-Progress-Report.docx",
    "examples/progress-report/Robot-Assembly-Progress-Report.pdf",
    "examples/research-plan/Robot_Assembly_Research_Plan.docx",
    "examples/research-plan/Robot_Assembly_Research_Plan.pdf",
})


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate manifest key: {key}")
        result[key] = value
    return result


def relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\x00" in value:
        raise ValueError("Paths must be nonempty repository-relative POSIX paths")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value:
        raise ValueError(f"Unsafe or noncanonical path: {value}")
    return path


def safe_path(root, relative, must_exist=False):
    path = root.joinpath(*relative.parts)
    current = root
    for component in relative.parts:
        current = current / component
        if current.is_symlink():
            raise ValueError(f"Symlinks are not allowed: {relative}")
    resolved = path.resolve(strict=must_exist)
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path leaves the selected root: {relative}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a regular file: {relative}")
    return path


def assemble(repository_root, output_root):
    repository_root = Path(repository_root).resolve(strict=True)
    output_root = Path(output_root)
    if output_root.is_symlink():
        raise ValueError("The output root must not be a symlink")
    output_root = output_root.resolve()
    if output_root.exists() and not output_root.is_dir():
        raise ValueError("The output root must be a directory")

    manifest_path = safe_path(repository_root, TRANSFER_DIR / "manifest.json", must_exist=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    if not isinstance(manifest, dict) or set(manifest) != {"files"}:
        raise ValueError("The manifest must contain only a files list")
    files = manifest["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= len(ALLOWED_TARGETS):
        raise ValueError("The manifest must describe one to four allowed files")

    validated = []
    seen_targets = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "bytes", "parts"}:
            raise ValueError("Each file must contain path, sha256, bytes and parts")
        target = relative_path(entry["path"])
        if str(target) not in ALLOWED_TARGETS or str(target) in seen_targets:
            raise ValueError(f"Unexpected or repeated target: {target}")
        seen_targets.add(str(target))
        size = entry["bytes"]
        digest = entry["sha256"]
        if type(size) is not int or size < 0:
            raise ValueError(f"Invalid byte count: {target}")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None:
            raise ValueError(f"Invalid SHA-256: {target}")
        if not isinstance(entry["parts"], list) or not entry["parts"]:
            raise ValueError(f"Missing parts: {target}")

        data = bytearray()
        for part in entry["parts"]:
            relative = relative_path(part)
            if relative.parts[:2] != TRANSFER_DIR.parts or len(relative.parts) < 3:
                raise ValueError(f"Chunk is outside the transfer directory: {part}")
            chunk = safe_path(repository_root, relative, must_exist=True)
            data.extend(chunk.read_bytes())
            if len(data) > size:
                raise ValueError(f"Byte count exceeds manifest: {target}")
        if len(data) != size:
            raise ValueError(f"Byte count does not match manifest: {target}")
        if hashlib.sha256(data).hexdigest() != digest.lower():
            raise ValueError(f"SHA-256 does not match manifest: {target}")
        destination = safe_path(output_root, target)
        validated.append((destination, data, digest.lower()))

    # No directories or output files are created until every entry is validated.
    for destination, data, digest in validated:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".sciwrite-", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(data)
            os.replace(temporary, destination)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        print(f"Verified and assembled {destination.relative_to(output_root)} ({len(data)} bytes, SHA-256 {digest})")
    return len(validated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, help="Write verified files under this directory for a local smoke test")
    arguments = parser.parse_args()
    repository_root = Path(__file__).resolve().parents[2]
    try:
        assemble(repository_root, arguments.output_root or repository_root)
    except (OSError, ValueError) as error:
        print(f"Transfer failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
