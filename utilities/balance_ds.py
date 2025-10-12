import os
import shutil
import random

def count_files_in_subdirs(base_dir):
    subdir_file_map = {}
    for subdir in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir)
        if os.path.isdir(subdir_path):
            files = [
                f for f in os.listdir(subdir_path)
                if os.path.isfile(os.path.join(subdir_path, f))
            ]
            subdir_file_map[subdir] = files
    return subdir_file_map

def sync_equal_files(base_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    subdir_file_map = count_files_in_subdirs(base_dir)

    # Determine minimum number of files among all subdirectories
    min_file_count = min(len(files) for files in subdir_file_map.values())

    for subdir, files in subdir_file_map.items():
        src_subdir_path = os.path.join(base_dir, subdir)
        dest_subdir_path = os.path.join(dest_dir, subdir)
        os.makedirs(dest_subdir_path, exist_ok=True)

        # Randomly select min_file_count files
        selected_files = random.sample(files, min_file_count)

        for file_name in selected_files:
            src_file = os.path.join(src_subdir_path, file_name)
            dest_file = os.path.join(dest_subdir_path, file_name)
            shutil.copy2(src_file, dest_file)

        print(f"{subdir}: Copied {min_file_count} files to {dest_subdir_path}")

if __name__ == "__main__":
    base_directory = "/home/t/tph777/classification/datasets/sdxl"  # Replace with your actual base directory path
    destination_directory = "/home/t/tph777/classification/datasets/sdxl_balanced"  # Replace with your desired destination path

    sync_equal_files(base_directory, destination_directory)
