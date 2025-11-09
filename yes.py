import os
import shutil
from pathlib import Path

def rebuild_dataset_with_resolution_captions():
    """Rebuild dataset from scratch with resolution-based captions"""
    
    # Local Mac paths
    base_path = "/Users/wongwh/Desktop/NUS/Y3S1/urop/NUSxTE_UROP"
    source_base = os.path.join(base_path, "datasets/new_set_with_vae/train")
    target_base = os.path.join(base_path, "dataset")
    images_dir = os.path.join(target_base, "images")
    control_dir = os.path.join(target_base, "control")
    
    # Clear and create target directories
    if os.path.exists(target_base):
        shutil.rmtree(target_base)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(control_dir, exist_ok=True)
    
    # Counter for sequential naming
    counter = 1
    
    print(f"Scanning source directory: {source_base}")
    
    # Check if source exists
    if not os.path.exists(source_base):
        print(f"❌ Source directory not found: {source_base}")
        print("Available directories in datasets/:")
        datasets_dir = os.path.join(base_path, "datasets")
        if os.path.exists(datasets_dir):
            for item in os.listdir(datasets_dir):
                print(f"  - {item}")
        return
    
    # Get all class folders (sorted for consistency)
    class_folders = sorted([f for f in os.listdir(source_base) 
                           if os.path.isdir(os.path.join(source_base, f))])
    
    for class_folder in class_folders:
        class_path = os.path.join(source_base, class_folder)
        
        print(f"\nProcessing class: {class_folder}")
        
        # Get all image files in this class folder
        image_files = []
        for file in os.listdir(class_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                image_files.append(file)
        
        # Sort files for consistency
        image_files.sort()
        
        print(f"Found {len(image_files)} images in {class_folder}")
        
        # Process each image
        for image_file in image_files:
            source_image = os.path.join(class_path, image_file)
            
            # Create sequential filename
            image_name = f"image_{counter:03d}.jpg"
            txt_name = f"image_{counter:03d}.txt"
            
            # Target paths
            target_image = os.path.join(images_dir, image_name)
            target_control = os.path.join(control_dir, image_name)
            target_txt = os.path.join(images_dir, txt_name)
            
            # Copy image to images/ and control/
            shutil.copy2(source_image, target_image)
            shutil.copy2(source_image, target_control)
            
            # Create txt file with resolution-based caption
            if image_file.startswith('generated'):
                caption = f"lower resolution {class_folder}"
            else:
                caption = f"higher resolution {class_folder}"
            
            with open(target_txt, 'w', encoding='utf-8') as f:
                f.write(caption)
            
            # Show progress
            if counter <= 5 or counter % 100 == 0:
                resolution_type = "lower" if image_file.startswith('generated') else "higher"
                print(f"  {counter:03d}: {image_file} -> {image_name} ({resolution_type} resolution {class_folder})")
            
            counter += 1
    
    total_images = counter - 1
    print(f"\n✅ Successfully processed {total_images} images!")
    print(f"Target structure:")
    print(f"├── images/ ({total_images} .jpg + {total_images} .txt files)")
    print(f"└── control/ ({total_images} .jpg files)")
    
    # Show some example captions
    print(f"\nExample captions created:")
    for i in range(1, min(4, total_images + 1)):
        txt_file = os.path.join(images_dir, f"image_{i:03d}.txt")
        if os.path.exists(txt_file):
            with open(txt_file, 'r') as f:
                caption = f.read().strip()
            print(f"  image_{i:03d}.txt: '{caption}'")

if __name__ == "__main__":
    rebuild_dataset_with_resolution_captions()