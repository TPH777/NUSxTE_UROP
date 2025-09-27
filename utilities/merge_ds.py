import os
import shutil

# Function to merge two directories
def merge_directories(src_dir, dest_dir):
    # Loop through all subdirectories in the source directory
    for subdir, dirs, files in os.walk(src_dir):
        # Get the relative path from the source directory to each subdirectory
        rel_path = os.path.relpath(subdir, src_dir)
        dest_subdir = os.path.join(dest_dir, rel_path)

        # Create corresponding subdirectory in the destination if it doesn't exist
        if not os.path.exists(dest_subdir):
            os.makedirs(dest_subdir)

        # Move or copy files from the source to destination subdirectory
        for file in files:
            src_file = os.path.join(subdir, file)
            dest_file = os.path.join(dest_subdir, file)

            # If you want to copy files:
            if not os.path.exists(dest_file):
                shutil.copy2(src_file, dest_file)
            else:
                print(f"File {file} already exists in {dest_subdir}. Skipping.")

# Define the source and destination directories
src_dir1 = '/home/t/tph777/training_set/train'
src_dir2 = '/home/t/tph777/sd3.5/inferred/v2'
dest_dir = '/home/t/tph777/classification/datasets/sd3.5'

# First, merge the contents of both directories into the destination
merge_directories(src_dir1, dest_dir)
merge_directories(src_dir2, dest_dir)

print("Directories merged successfully.")
