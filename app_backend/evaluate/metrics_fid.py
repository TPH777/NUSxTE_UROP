import os
import numpy as np
from PIL import Image
import tensorflow as tf
from scipy.linalg import sqrtm
from evaluate.util import load_images_from_class_directory, load_images_from_directory, preprocess_images

# --- Helper Functions ---
def extract_features(images_preprocessed, inception_model):
    """ Extracts features using InceptionV3 """
    features = inception_model.predict(images_preprocessed, batch_size=32)
    return features

def calculate_fid(real_features, generated_features, epsilon=1e-6):
    """ Calculates FID score between two feature sets """
    mu_real, sigma_real = np.mean(real_features, axis=0), np.cov(real_features, rowvar=False)
    mu_generated, sigma_generated = np.mean(generated_features, axis=0), np.cov(generated_features, rowvar=False)
    
    sigma_real += np.eye(sigma_real.shape[0]) * epsilon
    sigma_generated += np.eye(sigma_generated.shape[0]) * epsilon
    
    diff = mu_real - mu_generated
    covmean = sqrtm(sigma_real.dot(sigma_generated))
    
    if np.iscomplexobj(covmean):
        covmean = covmean.real
        
    fid = np.sum(diff**2) + np.trace(sigma_real + sigma_generated - 2 * covmean)
    return np.real(fid)

# --- FID Functions ---
def compute_overall_fid(real_images_path, generated_images_path, inception_model):
    """ Computes the overall FID score """
    real_images = load_images_from_directory(real_images_path)
    generated_images = load_images_from_directory(generated_images_path)
    
    if real_images.size == 0 or generated_images.size == 0:
        raise ValueError("Not enough images to compute Overall FID.")
        
    real_images_pre = preprocess_images(real_images)
    generated_images_pre = preprocess_images(generated_images)
    
    real_features = extract_features(real_images_pre, inception_model)
    generated_features = extract_features(generated_images_pre, inception_model)
    
    return calculate_fid(real_features, generated_features)

def compute_all_class_fids(real_dir, generated_dir, inception_model, target_size=(299, 299)):
    """ Computes FID scores for each class subdirectory """
    class_fid_scores = {}
    try:
        class_names = [d for d in os.listdir(real_dir) if os.path.isdir(os.path.join(real_dir, d))]
    except FileNotFoundError:
        return {} # Return empty if dir not found
        
    if not class_names:
        return {} # Return empty if no subdirs

    for class_name in class_names:
        real_class_dir = os.path.join(real_dir, class_name)
        generated_class_dir = os.path.join(generated_dir, class_name)
        
        if not os.path.exists(generated_class_dir):
            continue
        
        real_images = load_images_from_class_directory(real_class_dir, target_size)
        generated_images = load_images_from_class_directory(generated_class_dir, target_size)
        
        if real_images.size == 0 or generated_images.size == 0:
            continue
            
        real_images_pre = preprocess_images(real_images)
        generated_images_pre = preprocess_images(generated_images)
        
        real_features = extract_features(real_images_pre, inception_model)
        generated_features = extract_features(generated_images_pre, inception_model)
        
        fid_score = calculate_fid(real_features, generated_features)
        class_fid_scores[class_name] = fid_score

    return class_fid_scores