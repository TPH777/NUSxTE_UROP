# evaluate.py
import json
import os
import tensorflow as tf
import logging

# Import the specific metric functions
from evaluate.metrics_fid import compute_overall_fid, compute_all_class_fids
from evaluate.metrics_is import compute_inception_score
from evaluate.metrics_lpips import compute_class_lpips

def run_evaluation(name, real_images_path, generated_images_path):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_FILE = f"{BASE_DIR}/output/{name}/evaluate.log"
    log_dir = os.path.dirname(LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)

    METRICS_JSON = f"{BASE_DIR}/output/{name}/metrics.json"
    json_dir = os.path.dirname(METRICS_JSON)
    os.makedirs(json_dir, exist_ok=True)

    # --- 1. Setup Logging ---    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w')
        ]
    )

    logging.info(f"--- Starting Evaluation Run: {name} ---")

    
    all_metrics = {
        "inputs": {
            "real_path": real_images_path,
            "generated_path": generated_images_path,
        },
        "metrics": {}
    }

    # --- 2. Load Models ---
    try:
        inception_model_fid = tf.keras.applications.InceptionV3(include_top=False, weights='imagenet', pooling='avg')
        inception_model_is = tf.keras.applications.InceptionV3(include_top=True, weights='imagenet')
    except Exception as e:
        logging.error(f"Failed to load Inception models: {e}. Evaluation Halted.")
        return None # Cannot proceed

    # --- 3. Run Metric Stages ---

    # --- Stage 1: Inception Score ---
    logging.info("--- Stage 1: Calculating Inception Score ---")
    try:
        is_score = compute_inception_score(
            generated_images_path,
            inception_model_is
        )
        all_metrics["metrics"]["inception_score"] = is_score
    except Exception as e:
        all_metrics["metrics"]["inception_score"] = f"Error: {e}"

    # --- Stage 2: Overall FID (fid_single) ---
    logging.info("--- Stage 2: Calculating Overall FID ---")
    try:
        fid_overall_score = compute_overall_fid(
            real_images_path, 
            generated_images_path,
            inception_model_fid
        )
        all_metrics["metrics"]["fid_overall"] = fid_overall_score
    except Exception as e:
        all_metrics["metrics"]["fid_overall"] = f"Error: {e}"

    # --- Stage 3: Per-Class FID (fid_multi) ---
    logging.info("--- Stage 3: Calculating Per-Class FID ---")
    try:
        fid_class_scores = compute_all_class_fids(
            real_images_path, 
            generated_images_path,
            inception_model_fid
        )
        all_metrics["metrics"]["fid_per_class"] = fid_class_scores
    except Exception as e:
        all_metrics["metrics"]["fid_per_class"] = f"Error: {e}"

    # --- Stage 4: LPIPS Scores ---
    logging.info("--- Stage 4: Calculating LPIPS Scores ---")
    try:
        lpips_scores = compute_class_lpips(
            real_images_path,
            generated_images_path,
        )
        all_metrics["metrics"]["lpips_avg_min_per_class"] = lpips_scores
    except Exception as e:
        all_metrics["metrics"]["lpips_avg_min_per_class"] = f"Error: {e}"

    # --- 4. Save Results to JSON ---
    try:
        with open(METRICS_JSON, 'w') as f:
            json.dump(all_metrics, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving JSON file: {e}")
    
    logging.info(f"--- Complete Evaluation For '{name}' ---")
    return all_metrics