# metrics_is.py
import numpy as np
import tensorflow as tf
from scipy.stats import entropy

# Import helpers from the FID module to avoid code duplication
from metrics_fid import load_images_from_directory, preprocess_images

def compute_inception_score(directory_path, inception_model, batch_size=32):
    """ Computes the Inception Score for images in a directory """
    generated_images = load_images_from_directory(directory_path)
    if generated_images.size == 0:
        raise ValueError("No images found for Inception Score calculation.")
        
    images_pre = preprocess_images(generated_images)
    
    predictions = inception_model.predict(images_pre, batch_size=batch_size)
    
    # Calculate P(y|x) and P(y)
    p_y_x = predictions / np.sum(predictions, axis=1, keepdims=True)
    p_y = np.mean(p_y_x, axis=0)
    
    # Calculate KL divergence
    kl_div = np.mean([entropy(p, p_y) for p in p_y_x])
    
    # Inception Score
    is_score = np.exp(kl_div)
    return is_score