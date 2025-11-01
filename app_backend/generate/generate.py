from diffusers import DiffusionPipeline
import torch
import os

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
    LOG_FILE = os.path.join(OUTPUT_DIR, f"generate.log")

    # ==== Load pipeline and LoRA weights ====
    with open(LOG_FILE, "w") as f:
        try:
            f.write("Loading pipeline\n")

            pipe = DiffusionPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16
            )
            pipe.to("cuda")

            f.write("Loading LoRA weights\n")

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
                f.write(f"Saved: {img_path}\n")

            f.write("✅ Generation complete.\n")

        except Exception as e:
            error_msg = f"❌ Generation failed: {e}"
            f.write(error_msg + "\n")
