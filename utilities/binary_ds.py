import os
import shutil
from pathlib import Path

base_dir = '/home/t/tph777/sdxl/inferred/v1'
dest_dir = '/home/t/tph777/classification/datasets/sdxl'

def merge_ng_subdirectories(base_directory, destination_directory):
    """Merge all subdirectories with 'NG' prefix into a single 'NG' directory and copy others as-is."""
    
    base_path = Path(base_directory)
    dest_base = Path(destination_directory)

    # Create destination directory if it doesn't exist
    shutil.rmtree(dest_base, ignore_errors=True)
    dest_base.mkdir(parents=True, exist_ok=True)
    
    # Find all subdirectories
    all_subdirs = [d for d in base_path.iterdir() if d.is_dir()]
    ng_subdirs = [d for d in all_subdirs if d.name.startswith('NG')]
    non_ng_subdirs = [d for d in all_subdirs if not d.name.startswith('NG')]
    
    print(f"Found subdirectories with 'NG' prefix:")
    for subdir in ng_subdirs:
        print(f"  - {subdir.name}")
    
    print(f"\nFound subdirectories without 'NG' prefix:")
    for subdir in non_ng_subdirs:
        print(f"  - {subdir.name}")
    
    # Handle NG subdirectories - merge into single NG directory
    if ng_subdirs:
        ng_target = dest_base / "NG"
        ng_target.mkdir(exist_ok=True)
        
        print(f"\nMerging NG subdirectories into: {ng_target}")

        dir_index = 0  # To help with renaming files if needed
        for source_dir in ng_subdirs:
            print(f"Merging contents of {source_dir.name}...")
            
            # Copy all contents from source to NG directory
            for item in source_dir.iterdir():
                name = dir_index.__str__() + "_" + item.name
                dest_item_path = ng_target / name
                shutil.copy2(item, dest_item_path)
    
            dir_index += 1
    
    # Handle non-NG subdirectories - copy as-is
    print(f"\nCopying non-NG subdirectories to destination:")
    for source_dir in non_ng_subdirs:
        dest_dir = dest_base / source_dir.name
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
    
    print(f"\nProcessing completed!")
    print(f"- NG subdirectories merged into: {dest_base}/NG")
    print(f"- Non-NG subdirectories copied to: {dest_base}")

# Usage
if __name__ == "__main__":
    merge_ng_subdirectories(base_dir, dest_dir)