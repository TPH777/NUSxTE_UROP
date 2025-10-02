# Classification Results

This document contains the classification accuracy results for different image generation models and training approaches.

## Classification Accuracy Comparison

| Class                  | Original Dataset | VAE Model | SD3.5 + LoRA | SDXL + LoRA | SD1.5 + LORA |
| ---------------------- | ---------------- | --------- | ------------ | ----------- | ------------ |
| NG - Misalign          | 60.00%           | 40.00%    | 45.00%       | 35.00%      | 45.00%       |
| NG - No solder         | 70.00%           | 80.00%    | 70.00%       | 50.00%      | 60.00%       |
| NG - Not enough solder | 65.00%           | 80.00%    | 75.00%       | 70.00%      | 75.00%       |
| NG - Single            | 95.00%           | 90.00%    | 90.00%       | 100.00%     | 55.00%       |
| OK                     | 75.00%           | 75.00%    | 80.00%       | 100.00%     | 80.00%       |

### Model Details

- **Original Dataset Path:** `dataset/training_set`
- **VAE Generated Images:** `vae/beta-vae/Synthetic Images`
- **SD3.5 Generated Images:** `sd3.5/inferred/v2`
- **SDXL Generated Images:** `sdxl/inferred/v2`
- **SD1.5 Generated Images:** `sd1.5/inferred/v3`
