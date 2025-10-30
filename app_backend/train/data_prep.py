import os
import json

def generate_metadata_jsonl(root_dir):
    entries = []

    for subdir, dirs, files in os.walk(root_dir):
        rel_dir = os.path.relpath(subdir, root_dir)
        if rel_dir == ".":
            continue  # Skip root dir itself
        prompt = rel_dir.replace("\\", "/")  # Handle Windows paths

        for file in files:
            if file.lower().endswith('.jpg', '.jpeg', '.png', '.webp'):
                relative_path = os.path.join(prompt, file).replace("\\", "/")
                entry = {
                    "file_name": relative_path,
                    "text": prompt
                }
                entries.append(entry)

    with open(os.path.join(root_dir, 'metadata.jsonl'), 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')