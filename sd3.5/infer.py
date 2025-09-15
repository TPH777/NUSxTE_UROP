import torch
import os
from diffusers import StableDiffusion3Pipeline

print("Torch version:", torch.__version__)

model_path = "/home/t/tph777/sd3.5/output/v1"
output_dir = "/home/t/tph777/sd3.5/inferred/v1"
prompt = "NG - Not enough solder"

pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers", 
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

for i in range(5):
    image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]
    image.save(os.path.join(output_dir, f"{i}.png"))
