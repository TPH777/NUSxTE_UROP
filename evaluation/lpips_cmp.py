import os
import numpy as np
from PIL import Image
import argparse
import torch
import lpips  # Make sure to 'pip install lpips'
import shutil # Added for file copying

# --- Model and Device Setup ---
# Set up the device (use GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Load the LPIPS model (using AlexNet, which is standard)
# We set eval() mode as we are not training
lpips_model = lpips.LPIPS(net='alex').to(device).eval()
print(f"LPIPS model loaded on device: {device}")


# --- Image Loading Function ---

def load_and_preprocess_images_from_directory(directory_path, target_size=(256, 256)):
    """
    Loads all images from a directory, resizes them, and converts them
    to the PyTorch tensor format required for LPIPS:
    - Shape: (N, 3, H, W)
    - Normalized to [-1, 1]
    """
    image_tensors = []
    filenames = []
    
    if not os.path.exists(directory_path):
        return [], [] # Return empty lists if path doesn't exist

    for filename in os.listdir(directory_path):
        img_path = os.path.join(directory_path, filename)
        try:
            # Load, ensure 3 channels (RGB), and resize
            img = Image.open(img_path).convert('RGB')
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            img_np = np.array(img)
            
            # Convert to PyTorch tensor
            # (H, W, C) -> (C, H, W)
            img_tensor = torch.tensor(img_np, dtype=torch.float32).permute(2, 0, 1)
            
            # Normalize from [0, 255] to [-1, 1]
            img_tensor = (img_tensor / 255.0) * 2.0 - 1.0
            
            image_tensors.append(img_tensor)
            filenames.append(filename)
            
        except Exception as e:
            print(f"Could not load or process image {img_path}: {e}")
            
    return image_tensors, filenames


# --- LPIPS Computation Function ---

def compute_class_lpips(real_dir, generated_dir, output_dir, target_size=(256, 256)):
    """
    Computes LPIPS scores for each class by finding the nearest neighbor
    from the real set for each generated image.
    
    Also copies the generated images to output_dir, renamed by their score.
    """
    # Get all class subdirectories in the real images directory
    try:
        class_names = [d for d in os.listdir(real_dir) if os.path.isdir(os.path.join(real_dir, d))]
    except FileNotFoundError:
        print(f"Error: Real images directory not found at {real_dir}")
        return
        
    if not class_names:
        print(f"No class subdirectories found in {real_dir}")
        print("Running in flat directory mode (assuming images are in the root)...")
        class_names = [""] # Use empty string to represent the root directory itself

    for class_name in class_names:
        print(f"\n--- Processing Class: '{class_name if class_name else 'root'}' ---")
        
        real_class_dir = os.path.join(real_dir, class_name)
        generated_class_dir = os.path.join(generated_dir, class_name)
        
        # --- Create the new output directory for this class ---
        output_class_dir = os.path.join(output_dir, class_name)
        os.makedirs(output_class_dir, exist_ok=True)
        
        # Load real and generated images for the current class
        real_tensors, _ = load_and_preprocess_images_from_directory(real_class_dir, target_size)
        generated_tensors, generated_filenames = load_and_preprocess_images_from_directory(generated_class_dir, target_size)
        
        if not real_tensors:
            print(f"No real images found for class '{class_name}'. Skipping.")
            continue
        if not generated_tensors:
            print(f"No generated images found for class '{class_name}'. Skipping.")
            continue
            
        # Stack all real images into a single batch tensor on the GPU
        real_stack = torch.stack(real_tensors).to(device)
        print(f"Loaded {len(real_stack)} real images and {len(generated_tensors)} generated images.")

        all_minimum_scores = []

        # We don't need to track gradients, saving memory and computation
        with torch.no_grad():
            # Iterate through each generated image one by one
            for i, gen_tensor in enumerate(generated_tensors):
                gen_filename = generated_filenames[i]
                
                # Move the single generated image to the GPU
                gen_img = gen_tensor.to(device)
                
                # Expand generated image to match the batch size of the real stack
                gen_img_batch = gen_img.unsqueeze(0).expand_as(real_stack)
                
                # Compute LPIPS scores. 'scores' will be a tensor of N values.
                scores = lpips_model(gen_img_batch, real_stack)
                
                # Find the minimum score (i.e., the closest real image)
                min_score = torch.min(scores).item()
                all_minimum_scores.append(min_score)

                # --- NEW: Logic to copy and rename the file ---
                
                # 1. Get original file path
                original_file_path = os.path.join(generated_class_dir, gen_filename)
                
                # 2. Get file extension
                _, file_extension = os.path.splitext(gen_filename)
                
                # 3. Create new filename and handle potential collisions
                new_filename = f"{min_score:.6f}{file_extension}" # e.g., "0.123456.png"
                new_file_path = os.path.join(output_class_dir, new_filename)
                
                count = 1
                while os.path.exists(new_file_path):
                    # If "0.123456.png" exists, try "0.123456_1.png", etc.
                    new_filename = f"{min_score:.6f}_{count}{file_extension}"
                    new_file_path = os.path.join(output_class_dir, new_filename)
                    count += 1
                
                # 4. Copy the file
                try:
                    shutil.copy2(original_file_path, new_file_path)
                    print(f"  Image: {gen_filename:<30} | Min LPIPS: {min_score:.4f} | Saved as: {new_filename}")
                except Exception as e:
                    print(f"  Image: {gen_filename:<30} | Min LPIPS: {min_score:.4f} | FAILED to copy: {e}")

        # Calculate the average of all the minimums for this class
        if all_minimum_scores:
            average_of_minimums = np.mean(all_minimum_scores)
            print(f"--- Average Min LPIPS for class '{class_name}': {average_of_minimums:.4f} ---")
        else:
            print(f"--- No scores computed for class '{class_name}' ---")


# --- Main Function ---

def main():
    parser = argparse.ArgumentParser(description="Compute per-image LPIPS and save renamed copies")
    parser.add_argument('--real_images_path', type=str, required=True, help="Path to real images directory (can contain class subdirs)")
    parser.add_argument('--generated_images_path', type=str, required=True, help="Path to generated images directory (must match real's class subdirs)")
    parser.add_argument('--output_dir', type=str, required=True, help="Path to save the renamed copies")
    args = parser.parse_args()
    
    real_images_dir = args.real_images_path
    generated_images_dir = args.generated_images_path
    output_dir = args.output_dir
    
    # Create the base output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving renamed images to: {output_dir}")
    
    compute_class_lpips(real_images_dir, generated_images_dir, output_dir)

if __name__ == "__main__":
    # Remember to rename this file to something other than 'lpips.py'
    # e.g., 'run_lpips_eval.py'
    main()