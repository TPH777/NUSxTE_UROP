import os
import argparse

# Define the image file extensions to look for
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

def create_text_files_for_images(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                image_path = os.path.join(subdir, file)
                image_name, _ = os.path.splitext(file)
                parent_dir_name = os.path.basename(subdir)
                
                # Create the text file path
                text_file_path = os.path.join(subdir, f"{image_name}.txt")
                
                # Write the directory name into the text file
                with open(text_file_path, 'w') as txt_file:
                    txt_file.write(parent_dir_name)
                
                print(f"Created: {text_file_path} with content: {parent_dir_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create .txt files for each image, containing the parent directory name.")
    parser.add_argument("root_dir", help="Path to the root directory containing images.")
    args = parser.parse_args()
    create_text_files_for_images(args.root_dir)
