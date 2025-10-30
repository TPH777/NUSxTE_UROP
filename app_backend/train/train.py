import subprocess
import os
from data_prep import generate_metadata_jsonl

def train_model(
    name: str,
    dataset_path: str,              
    batch_size: int,                # Default: 4  
    learning_rate: float,           # Default: 1e-4
    epochs: int,                    # Default: 10
    resolution: int,                # Default: 512
    memory_efficient: bool          # Default: False
):
    # ==== Initialisation ====
    # Constants
    MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
    VAE = "madebyollin/sdxl-vae-fp16-fix"
    ACCELERATE_CONFIG = "accelerate_config.yaml"
    LOG_FILE = os.path.join(OUTPUT_DIR, f"train_output.log")

    # Output directory
    OUTPUT_DIR = f"output/{name}"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate metadata.jsonl
    generate_metadata_jsonl(dataset_path)

    # ==== Build accelerate command ====
    cmd = [
        "accelerate", "launch",
        "--config_file", ACCELERATE_CONFIG,
        "train_text_to_image_lora_sdxl.py",
        f"--pretrained_model_name_or_path={MODEL}",
        f"--pretrained_vae_model_name_or_path={VAE}",
        f"--train_data_dir={dataset_path}",
        f"--resolution={resolution}",
        f"--train_batch_size={batch_size}",
        f"--num_train_epochs={epochs}",
        f"--learning_rate={learning_rate}",
        f"--output_dir={OUTPUT_DIR}"
    ]

    # Optional flags
    if memory_efficient:
        cmd.append("--enable_xformers_memory_efficient_attention")

    # ==== Run and stream output ====
    with open(LOG_FILE, "w") as f:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")  # show live in terminal
            f.write(line)
        process.wait()