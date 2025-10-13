import os
import numpy as np
from PIL import Image
import tensorflow as tf
from scipy.linalg import sqrtm

# Load images from directory
def load_images_from_directory(directory_path, target_size=(299, 299)):
    images = []
    for subdir in os.listdir(directory_path):
        subdir_path = os.path.join(directory_path, subdir)
        if os.path.isdir(subdir_path):
            for filename in os.listdir(subdir_path):
                img_path = os.path.join(subdir_path, filename)
                try:
                    img = Image.open(img_path)
                    img = img.resize(target_size)
                    img = np.array(img)
                    if img.shape == (299, 299, 3):
                        images.append(img)
                except Exception as e:
                    print(f"Could not load image {img_path}: {e}")
    return np.array(images)

# Preprocess images
def preprocess_images(images):
    images = tf.convert_to_tensor(images, dtype=tf.float32)
    images = tf.image.resize(images, (299, 299))
    images = tf.keras.applications.inception_v3.preprocess_input(images)
    return images

# Extract features from InceptionV3
def extract_features(images, inception_model):
    features = inception_model.predict(images)
    return features

# Calculate FID
def calculate_fid(real_features, generated_features):
    mu_real, sigma_real = np.mean(real_features, axis=0), np.cov(real_features, rowvar=False)
    mu_generated, sigma_generated = np.mean(generated_features, axis=0), np.cov(generated_features, rowvar=False)
    diff = mu_real - mu_generated
    covmean = sqrtm(sigma_real.dot(sigma_generated))
    fid = np.sum(diff**2) + np.trace(sigma_real + sigma_generated - 2 * covmean)
    return fid

# Main function to compute FID
def compute_fid(real_images_path, generated_images_path):
    # Load real and generated images
    real_images = load_images_from_directory(real_images_path)
    generated_images = load_images_from_directory(generated_images_path)
    
    # Preprocess images
    real_images_preprocessed = preprocess_images(real_images)
    generated_images_preprocessed = preprocess_images(generated_images)
    
    # Load pre-trained InceptionV3 model
    inception_model = tf.keras.applications.InceptionV3(include_top=False, pooling='avg')
    
    # Extract features
    real_features = extract_features(real_images_preprocessed, inception_model)
    generated_features = extract_features(generated_images_preprocessed, inception_model)
    
    # Compute FID
    fid_value = calculate_fid(real_features, generated_features)
    print(f"FID: {np.real(fid_value)}")

# Example usage
real_images_path = "/home/t/tph777/extended_set/newprompt_ds/test"
generated_images_path = "/home/t/tph777/sdxl/inferred/v6"
compute_fid(real_images_path, generated_images_path)
