import os
from pathlib import Path
import shutil

IMAGE_DIR = Path("dataset/images")
CAPTION_TEXT = "make it higher resolution, metal NG - Not enough solder"
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

def main():
    if not IMAGE_DIR.exists():
        raise SystemExit(f"Missing folder: {IMAGE_DIR}")

    files = [p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in IMG_EXTS]
    files.sort()

    if not files:
        print("No images found.")
        return

    # Safety: move originals to a temp folder first
    backup_dir = IMAGE_DIR / "_backup_originals"
    backup_dir.mkdir(exist_ok=True)

    # Map old -> new
    planned = []
    for idx, p in enumerate(files, start=1):
        new_stem = f"image_{idx:03d}"
        new_name = new_stem + p.suffix.lower()
        planned.append((p, IMAGE_DIR / new_name))

    # Detect collisions
    targets = [t for _, t in planned]
    if len(set(t.name for t in targets)) != len(targets):
        raise SystemExit("Collision detected in target names; aborting.")

    # Move originals into backup then place renamed copies
    for old, new in planned:
        tmp = backup_dir / old.name
        if not tmp.exists():
            shutil.move(str(old), str(tmp))
        shutil.copy2(tmp, new)
        txt_file = IMAGE_DIR / (new.stem + ".txt")
        txt_file.write_text(CAPTION_TEXT, encoding="utf-8")

    print(f"Renamed {len(planned)} images.")
    print(f"Originals kept in: {backup_dir}")
    print("Done.")

if __name__ == "__main__":
    main()