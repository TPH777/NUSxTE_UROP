import os
import json

def generate_metadata_jsonl(root_dir):
    entries = []
    allowed = ('.jpg', '.jpeg', '.png', '.webp')
    label = os.path.basename(os.path.normpath(root_dir))

    for fname in os.listdir(root_dir):
        path = os.path.join(root_dir, fname)
        if os.path.isfile(path) and fname.lower().endswith(allowed):
            entry = {
                "file_name": fname,
                "text": label
            }
            entries.append(entry)

    out_path = os.path.join(root_dir, 'metadata.jsonl')
    with open(out_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    return out_path, len(entries)