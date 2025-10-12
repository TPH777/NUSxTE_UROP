import os
import numpy as np
from PIL import Image
import tensorflow as tf
from scipy.linalg import sqrtm

# Load pre-trained InceptionV3 model
inception_model = tf.keras.applications.InceptionV3(include_top=False, weights='imagenet', pooling='avg')

# Function to load images and extract features from a specific directory
def load_images_from_directory(directory_path, target_size=(299, 299)):
    images = []
    for filename in os.listdir(directory_path):
        img_path = os.path.join(directory_path, filename)
        try:
            img = Image.open(img_path)
            img = img.resize(target_size)  # Resize image to 299x299
            img = np.array(img)
            if img.shape == (299, 299, 3):  # Ensure it's a 3-channel image
                images.append(img)
        except Exception as e:
            print(f"Could not load image {img_path}: {e}")
    return np.array(images)

# Function to compute FID
def calculate_fid(real_features, generated_features, epsilon=1e-6):
    # Calculate mean and covariance of the features for real and generated images
    mu_real, sigma_real = np.mean(real_features, axis=0), np.cov(real_features, rowvar=False)
    mu_generated, sigma_generated = np.mean(generated_features, axis=0), np.cov(generated_features, rowvar=False)
    
    # Regularize covariance matrices by adding small value to the diagonal
    sigma_real += np.eye(sigma_real.shape[0]) * epsilon
    sigma_generated += np.eye(sigma_generated.shape[0]) * epsilon
    
    # Compute the Fréchet distance
    diff = mu_real - mu_generated
    covmean = sqrtm(sigma_real.dot(sigma_generated))
    
    # If the result is complex, take the real part
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    
    fid = np.sum(diff**2) + np.trace(sigma_real + sigma_generated - 2 * covmean)
    return fid

# Function to extract features from images using InceptionV3
def extract_inception_features(images):
    images = tf.convert_to_tensor(images, dtype=tf.float32)
    images = tf.image.resize(images, (299, 299))  # Resize to InceptionV3 input size
    images = tf.keras.applications.inception_v3.preprocess_input(images)  # Preprocess for InceptionV3
    
    features = inception_model.predict(images)
    return features

# Function to compute FID for each class
def compute_class_fid(real_dir, generated_dir, target_size=(299, 299)):
    # Get all class subdirectories in the real images directory
    class_names = [d for d in os.listdir(real_dir) if os.path.isdir(os.path.join(real_dir, d))]
    
    for class_name in class_names:
        # Load real and generated images for the current class
        real_class_dir = os.path.join(real_dir, class_name)
        generated_class_dir = os.path.join(generated_dir, class_name)
        
        if not os.path.exists(generated_class_dir):
            print(f"Generated images for class {class_name} not found!")
            continue
        
        real_images = load_images_from_directory(real_class_dir, target_size)
        generated_images = load_images_from_directory(generated_class_dir, target_size)
        
        # Extract InceptionV3 features for real and generated images
        real_features = extract_inception_features(real_images)
        generated_features = extract_inception_features(generated_images)
        
        # Compute FID score for the current class
        fid_score = calculate_fid(real_features, generated_features)
        print(f"FID for class '{class_name}': {fid_score}")

# Main function to run the FID computation
def main():
    real_images_dir = "/home/t/tph777/extended_set/testP"
    generated_images_dir = "/home/t/tph777/sdxl/inferred/v5"
    compute_class_fid(real_images_dir, generated_images_dir)

if __name__ == "__main__":
    main()
