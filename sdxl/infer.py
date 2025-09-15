from diffusers import DiffusionPipeline
import torch
import os

print("Torch version:", torch.__version__)

model_path = "./output/sdxl-finetuned3"
dataset_dir = "./dataset1"
output_root_dir = "./inferred/run1"

pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
)
pipe.to("cuda")

pipe.load_lora_weights(
    model_path,
    weight_name="pytorch_lora_weights.safetensors",
    adapter_name="custom_lora",
    prefix=None  # Set to None only if your LoRA was trained/saved accordingly
)
pipe.set_adapters(["custom_lora"])

for subdir, dirs, files in os.walk(dataset_dir):
    rel_dir = os.path.relpath(subdir, dataset_dir)
    if rel_dir == ".":
        continue  # Skip root dir
    prompt = rel_dir.replace("\\", "/")  # For Windows compatibility

    output_dir = os.path.join(output_root_dir, prompt)
    os.makedirs(output_dir, exist_ok=True)

    for i in range(5):
        image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]
        image.save(os.path.join(output_dir, f"{i}.png"))
