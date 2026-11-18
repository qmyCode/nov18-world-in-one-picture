#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261118 competition.

The front-page poster for Wednesday 18 November 2026 is committed in
this repository as entry.png (drawn programmatically by draw.py, a
build tool that is not part of the run). This program's whole job is
to place that exact image at /output/entry.png, byte for byte, so the
submission renders identically on every run.

Standard library only; no network; deterministic.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
OUTPUT_DIR = "/output"
OUTPUT = os.path.join(OUTPUT_DIR, "entry.png")

MAX_BYTES = 1024 * 1024  # competition cap: the image must fit in 1 MiB
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"


def check_image(path: str) -> int:
    """Return the byte size of a valid PNG/JPEG at path, or raise ValueError."""
    size = os.path.getsize(path)
    if size == 0:
        raise ValueError(f"{path} is empty")
    if size > MAX_BYTES:
        raise ValueError(f"{path} is {size} bytes, over the 1 MiB cap")
    with open(path, "rb") as fh:
        head = fh.read(len(PNG_SIGNATURE))
    if head != PNG_SIGNATURE and not head.startswith(JPEG_SIGNATURE):
        raise ValueError(f"{path} carries no PNG or JPEG signature")
    return size


def main() -> int:
    if not os.path.isfile(SOURCE):
        print(f"error: committed image not found at {SOURCE}", file=sys.stderr)
        return 1
    try:
        expected = check_image(SOURCE)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        shutil.copyfile(SOURCE, OUTPUT)
        written = check_image(OUTPUT)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if written != expected:
        print(f"error: copy drifted ({expected} -> {written} bytes)", file=sys.stderr)
        return 1
    print(f"entry.png: {written} bytes, signature and size verified, written to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
