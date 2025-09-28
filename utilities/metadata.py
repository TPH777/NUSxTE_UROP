import os
import json

def generate_metadata_jsonl(root_dir, output_file='metadata.jsonl', image_extensions=('.jpg', '.jpeg', '.png', '.webp')):
    entries = []

    for subdir, dirs, files in os.walk(root_dir):
        rel_dir = os.path.relpath(subdir, root_dir)
        if rel_dir == ".":
            continue  # Skip root dir itself
        prompt = rel_dir.replace("\\", "/")  # Handle Windows paths

        for file in files:
            if file.lower().endswith(image_extensions):
                relative_path = os.path.join(prompt, file).replace("\\", "/")
                entry = {
                    "file_name": relative_path,
                    "text": prompt
                }
                entries.append(entry)

    with open(os.path.join(root_dir, output_file), 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"✅ metadata.jsonl written with {len(entries)} entries.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate metadata.jsonl for Hugging Face Diffusers training.")
    parser.add_argument("dataset_dir", help="Path to the dataset root directory.")
    parser.add_argument("--output", default="metadata.jsonl", help="Output JSONL filename.")
    args = parser.parse_args()

    generate_metadata_jsonl(args.dataset_dir, args.output)
