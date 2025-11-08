from diffusers import DiffusionPipeline
import torch
import os
import datetime
import shutil

def generate(
    name: str,
    num_samples: int,
    prompt: str,  
    resolution: int,                         # Default: 512
    num_inference_steps: int,                # Default: 50
    guidance_scale: float                    # Default: 7.5
):
    # ==== Initialisation ====
    # Constants
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TRAINED_MODEL = f"{BASE_DIR}/../train/output/{name}/{prompt.replace(' ', '_')}/"

    # Output directory
    OUTPUT_DIR = f"{BASE_DIR}/output/{name}/{prompt.replace(' ', '_')}"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # keep a main log in the module dir and copy a backup into the output dir
    LOG_FILE = os.path.join(BASE_DIR, "generate.log")
    # To copy the logfile for tracking as a backup within the class
    backup_log = os.path.join(OUTPUT_DIR, "generate.log")

    # ==== Load pipeline and LoRA weights ====
    # open with explicit encoding and line buffering, and flush after each write to ensure live logging
    with open(LOG_FILE, "w", encoding="utf-8", buffering=1) as f:
        def _ts():
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        
        def log(msg: str):
            f.write(f"{_ts()} [INFO] --- {msg}\n")
            f.flush()
        
        try:
            log("Loading pipeline")
 
            pipe = DiffusionPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16
            )
            pipe.to("cuda")
 
            log("Loading LoRA weights")
 
            pipe.load_lora_weights(
                TRAINED_MODEL,
                weight_name="pytorch_lora_weights.safetensors",
                adapter_name="custom_lora",
                prefix=None
            )
            pipe.set_adapters(["custom_lora"])
 
            # ==== Generate images ====
            for i in range(num_samples):
                image = pipe(
                    prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=resolution,
                    width=resolution
                ).images[0]
 
                img_path = os.path.join(OUTPUT_DIR, f"{i}.png")
                image.save(img_path)
                log(f"Saved image {i+1}/{num_samples}")

            shutil.copy2(LOG_FILE, backup_log)
            log(f"Complete Generation For '{name}'")

        except Exception as e:
            log(f"Failed Generation For '{name}': {e}")