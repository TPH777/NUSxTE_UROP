# Classification Results

This document contains the classification accuracy results for different image generation models and training approaches.

## Original Dataset Performance

**Dataset Path:** `dataset/training_set`

| Class                  | Accuracy |
| ---------------------- | -------- |
| NG - Misalign          | 60.00%   |
| NG - No solder         | 70.00%   |
| NG - Not enough solder | 65.00%   |
| NG - Single            | 95.00%   |
| OK                     | 75.00%   |

## VAE Model Results

**Image Generation Model:** VAE  
**Output Images Path:** `vae/beta-vae/Synthetic Images`

| Class                  | Accuracy |
| ---------------------- | -------- |
| NG - Misalign          | 40.00%   |
| NG - No solder         | 80.00%   |
| NG - Not enough solder | 80.00%   |
| NG - Single            | 90.00%   |
| OK                     | 75.00%   |

## Stable Diffusion 3.5 + LoRA Results

**Image Generation Model:** SD3.5 + LoRA  
**Output Images Path:** `sd3.5/inferred/v2`

| Class                  | Accuracy |
| ---------------------- | -------- |
| NG - Misalign          | 45.00%   |
| NG - No solder         | 70.00%   |
| NG - Not enough solder | 75.00%   |
| NG - Single            | 90.00%   |
| OK                     | 80.00%   |
