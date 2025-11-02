# metrics_lpips.py
import os
import numpy as np
from PIL import Image
import torch
import lpips

# --- Model and Device Setup ---
# Load the LPIPS model once on import
try:
    LPIPS_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    LPIPS_MODEL = lpips.LPIPS(net='alex').to(LPIPS_DEVICE).eval()
except Exception:
    LPIPS_MODEL = None
    LPIPS_DEVICE = None

# --- Image Loading Function ---
def load_lpips_images(directory_path, target_size=(256, 256)):
    """ Loads and preprocesses images for LPIPS """
    image_tensors = []
    
    if not os.path.exists(directory_path):
        return []

    for filename in os.listdir(directory_path):
        img_path = os.path.join(directory_path, filename)
        try:
            img = Image.open(img_path).convert('RGB')
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            img_np = np.array(img)
            # (H, W, C) -> (C, H, W)
            img_tensor = torch.tensor(img_np, dtype=torch.float32).permute(2, 0, 1)
            # Normalize from [0, 255] to [-1, 1]
            img_tensor = (img_tensor / 255.0) * 2.0 - 1.0
            image_tensors.append(img_tensor)
        except Exception:
            pass # Ignore failed image loads
            
    return image_tensors

# --- LPIPS Computation Function ---
def compute_class_lpips(real_dir, generated_dir, target_size=(256, 256)):
    """ Computes per-class LPIPS scores (min distance avg) """
    if LPIPS_MODEL is None:
        raise ImportError("LPIPS model is not loaded. Skipping LPIPS calculation.")

    all_class_scores = {}
    try:
        class_names = [d for d in os.listdir(real_dir) if os.path.isdir(os.path.join(real_dir, d))]
    except FileNotFoundError:
        return {}
        
    if not class_names:
        class_names = [""] # Assume flat directory structure

    for class_name in class_names:
        class_label = class_name if class_name else 'root'
        
        real_class_dir = os.path.join(real_dir, class_name)
        generated_class_dir = os.path.join(generated_dir, class_name)
        
        real_tensors = load_lpips_images(real_class_dir, target_size)
        generated_tensors = load_lpips_images(generated_class_dir, target_size)
        
        if not real_tensors or not generated_tensors:
            continue
            
        real_stack = torch.stack(real_tensors).to(LPIPS_DEVICE)

        all_minimum_scores = []

        with torch.no_grad():
            for gen_tensor in generated_tensors:
                gen_img = gen_tensor.to(LPIPS_DEVICE)
                gen_img_batch = gen_img.unsqueeze(0).expand(real_stack.shape[0], -1, -1, -1)
                
                scores = LPIPS_MODEL(gen_img_batch, real_stack)
                min_score = torch.min(scores).item()
                all_minimum_scores.append(min_score)

        if all_minimum_scores:
            average_of_minimums = np.mean(all_minimum_scores)
            all_class_scores[class_label] = average_of_minimums
        else:
            all_class_scores[class_label] = None
            
    return all_class_scores