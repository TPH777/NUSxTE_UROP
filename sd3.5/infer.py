import torch
import os
from diffusers import StableDiffusion3Pipeline

print("Torch version:", torch.__version__)

version = "v3"
num_samples = 30
resolution = 384
output_root_dir = f"/home/t/tph777/sd3.5/inferred/{version}"
model_root_dir = f"/home/t/tph777/sd3.5/output/{version}"

pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers", 
    torch_dtype=torch.float16
)
pipe.to("cuda")

for item in os.listdir(model_root_dir):
    item_path = os.path.join(model_root_dir, item)
    if os.path.isdir(item_path):
        prompt = item
        print("Processing prompt:", prompt)
        model_path = os.path.join(model_root_dir, prompt)
        output_dir = os.path.join(output_root_dir, prompt)
        os.makedirs(output_dir, exist_ok=True)

        pipe.load_lora_weights(
            model_path,
            weight_name="pytorch_lora_weights.safetensors",
            prefix=None
        )

        for i in range(num_samples):
            image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5, height=resolution, width=resolution).images[0]
            image.save(os.path.join(output_dir, f"{i}.png"))