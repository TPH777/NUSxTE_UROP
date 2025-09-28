from diffusers import QwenImageEditPipeline
import torch
from PIL import Image

# Load the pipeline
pipeline = QwenImageEditPipeline.from_pretrained("Qwen/Qwen-Image-Edit-2509")
pipeline.to(torch.bfloat16)
pipeline.to("cuda")

# Load trained LoRA weights
pipeline.load_lora_weights("/home/w/weng/test/flymyai-lora-trainer/test_lora_saves_edit-single-onepic/checkpoint-3000/pytorch_lora_weights.safetensors")

# Load input image
image = Image.open("/home/w/weng/test/flymyai-lora-trainer/QI_edit_validation_single/0.96503084897995_20250113_002339_329.jpg").convert("RGB")

# Define editing prompt
prompt = "make it higher resolution, metal NG - Single"

# Generate edited image
inputs = {
    "image": image,
    "prompt": prompt,
    "generator": torch.manual_seed(0),
    "true_cfg_scale": 4.0,
    "negative_prompt": " ",
    "num_inference_steps": 50,
}

with torch.inference_mode():
    output = pipeline(**inputs)
    output_image = output.images[0]
    output_image.save("edited_image.png")