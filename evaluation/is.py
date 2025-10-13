import os
import numpy as np
from PIL import Image
import tensorflow as tf
from scipy.stats import entropy
import argparse

# Load pre-trained InceptionV3 model
inception_model = tf.keras.applications.InceptionV3(include_top=True, weights='imagenet')

def load_images_from_directory(directory_path, target_size=(299, 299)):
    images = []
    for subdir in os.listdir(directory_path):
        subdir_path = os.path.join(directory_path, subdir)
        if os.path.isdir(subdir_path):
            for filename in os.listdir(subdir_path):
                img_path = os.path.join(subdir_path, filename)
                try:
                    img = Image.open(img_path)
                    img = img.resize(target_size)  # Resize image to 299x299
                    img = np.array(img)
                    if img.shape == (299, 299, 3):  # Ensure it's a 3-channel image
                        images.append(img)
                except Exception as e:
                    print(f"Could not load image {img_path}: {e}")
    return np.array(images)

def inception_score(images, num_classes=1000):
    # Preprocess images for InceptionV3 model
    images = tf.convert_to_tensor(images, dtype=tf.float32)
    images = tf.image.resize(images, (299, 299))  # InceptionV3 input size
    images = tf.keras.applications.inception_v3.preprocess_input(images)
    
    # Get the predictions for the images
    predictions = inception_model.predict(images)
    
    # Calculate P(y|x) and P(y)
    p_y_x = predictions / np.sum(predictions, axis=1, keepdims=True)  # Normalize to get probabilities
    p_y = np.mean(p_y_x, axis=0)  # Marginal distribution
    
    # Calculate KL divergence
    kl_div = np.mean([entropy(p, p_y) for p in p_y_x])  # Calculate KL for each image
    
    # Inception Score
    is_score = np.exp(kl_div)
    return is_score

def get_inception_score(directory_path):
    # Load the images
    generated_images = load_images_from_directory(directory_path)

    # If you have a large dataset, you may want to randomly sample from it:
    # generated_images = generated_images[np.random.choice(generated_images.shape[0], 1000, replace=False)]

    # Calculate Inception Score
    inception_score_value = inception_score(generated_images)
    print(f"Inception Score: {inception_score_value}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory_path", required=True)
    
    args = parser.parse_args()
    get_inception_score(args.directory_path)

