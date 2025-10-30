from diffusers import DiffusionPipeline
import torch
import os

def generate(
    name: str,
    num_samples: int,
    classes: list[str],  
    resolution: int,                         # Default: 512
    num_inference_steps: int,                # Default: 50
    guidance_scale: float                    # Default: 7.5
):
    # ==== Initialisation ====
    # Constants
    TRAINED_MODEL = f"../train/output/{name}"
    LOG_FILE = os.path.join(GENERATED_DIR, f"generate.log")

    # Output directory
    GENERATED_DIR = f"generated/{name}"
    os.makedirs(GENERATED_DIR, exist_ok=True)

    # ==== Load pipeline and LoRA weights ====
    with open(LOG_FILE, "w") as f:
        try:
            f.write("Loading pipeline...\n")

            pipe = DiffusionPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16
            )
            pipe.to("cuda")

            f.write("Loading LoRA weights...\n")

            pipe.load_lora_weights(
                TRAINED_MODEL,
                weight_name="pytorch_lora_weights.safetensors",
                adapter_name="custom_lora",
                prefix=None
            )
            pipe.set_adapters(["custom_lora"])

            # ==== Generate images for each class ====
            for prompt in classes:
                output_dir = os.path.join(GENERATED_DIR, prompt)
                os.makedirs(output_dir, exist_ok=True)

                f.write(f"Generating for prompt: {prompt}\n")

                for i in range(num_samples):
                    image = pipe(
                        prompt,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        height=resolution,
                        width=resolution
                    ).images[0]

                    img_path = os.path.join(output_dir, f"{i}.png")
                    image.save(img_path)
                    f.write(f"Saved: {img_path}\n")

            print(f"\n✅ Generation complete! Images saved to: {GENERATED_DIR}\n")
            f.write("✅ Generation complete.\n")

        except Exception as e:
            error_msg = f"❌ Generation failed: {e}"
            f.write(error_msg + "\n")
