#!/usr/bin/env python3
"""
Build a Qwen Image Edit LoRA-style dataset folder:

dataset/
  images/
    image_001.jpg
    image_001.txt  # caption
    ...
  control/
    image_001.jpg  # control image (mirrors target unless custom control is provided)

Reads: datasets/v1_cut/metadata.jsonl with entries of the form
{"file_name": "OK/xxx.jpg", "text": "OK"}

Creates: dataset/images, dataset/control, and dataset/index.csv mapping.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import copy2


REPO_ROOT = Path(__file__).resolve().parents[1]
METADATA = REPO_ROOT / "datasets" / "v1_cut" / "metadata.jsonl"
SRC_ROOT = REPO_ROOT / "datasets" / "v1_cut"
OUT_ROOT = REPO_ROOT / "dataset"
IMAGES_DIR = OUT_ROOT / "images"
CONTROL_DIR = OUT_ROOT / "control"


@dataclass
class Item:
    rel_path: Path
    caption: str


def read_metadata(path: Path) -> list[Item]:
    items: list[Item] = []
    with path.open("r", encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"WARN: Skipping invalid JSON on line {ln}: {e}")
                continue
            rel = Path(obj["file_name"])  # relative to SRC_ROOT
            caption = str(obj.get("text", "")).strip()
            items.append(Item(rel_path=rel, caption=caption))
    return items


def zero_pad_width(n: int) -> int:
    return max(3, len(str(n)))


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        # Do not recursively delete to be conservative; remove contents we control
        for child in path.iterdir():
            if child.is_file():
                child.unlink(missing_ok=True)
            elif child.is_dir():
                # only clear known subdirs
                for sub in child.rglob("*"):
                    if sub.is_file():
                        sub.unlink(missing_ok=True)
                # leave directories in place
    else:
        path.mkdir(parents=True, exist_ok=True)


def main(argv: list[str]) -> int:
    if not METADATA.exists():
        print(f"ERROR: metadata file not found: {METADATA}")
        return 2
    items = read_metadata(METADATA)
    if not items:
        print("ERROR: No items found in metadata.jsonl")
        return 3

    # Prepare output dirs
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    ensure_clean_dir(IMAGES_DIR)
    ensure_clean_dir(CONTROL_DIR)

    width = zero_pad_width(len(items))
    index_rows: list[dict[str, str]] = []

    missing = 0
    for i, item in enumerate(items, start=1):
        src = SRC_ROOT / item.rel_path
        if not src.exists():
            print(f"WARN: source missing, skipping: {src}")
            missing += 1
            continue
        suffix = src.suffix.lower() or ".jpg"
        stem = f"image_{i:0{width}d}"
        tgt_img = IMAGES_DIR / f"{stem}{suffix}"
        ctl_img = CONTROL_DIR / f"{stem}{suffix}"
        cap_file = IMAGES_DIR / f"{stem}.txt"

        # Copy images
        copy2(src, tgt_img)
        copy2(src, ctl_img)  # mirror as control by default

        # Write caption
        caption = item.caption if item.caption else ""
        cap_file.write_text(caption + "\n", encoding="utf-8")

        index_rows.append(
            {
                "index": f"{i}",
                "image_file": tgt_img.relative_to(OUT_ROOT).as_posix(),
                "control_file": ctl_img.relative_to(OUT_ROOT).as_posix(),
                "caption_file": cap_file.relative_to(OUT_ROOT).as_posix(),
                "caption": caption,
                "source_relpath": item.rel_path.as_posix(),
            }
        )

    # Write index CSV
    with (OUT_ROOT / "index.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "index",
                "image_file",
                "control_file",
                "caption_file",
                "caption",
                "source_relpath",
            ],
        )
        writer.writeheader()
        writer.writerows(index_rows)

    print(
        f"Done. Wrote {len(index_rows)} items to {OUT_ROOT}. "
        + (f"Missing: {missing}." if missing else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
