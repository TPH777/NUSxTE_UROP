# Classification Methodology

# Methodology

1. **Initial dataset:** 10 training images, 20 testing images for each class
2. **Baseline:** Train classification model with the 10 training images and test with the 20 to get baseline accuracy
3. **Generation:** Train generative model with the initial dataset training images (10) to produce 30 additional images for each class
4. **Retraining:** Retrain classification model with 10+30=40 training images
5. **Evaluation:** Test the new model with the same 20 images and compare with baseline accuracy

---

# Training Set Dataset Results

## Multi-Class Classification Accuracy Comparison

| Class                  | Original Dataset                           | VAE Model                                              | SD3.5 + LoRA                            | SDXL + LoRA                            | SD1.5 + LORA                            |
| ---------------------- | ------------------------------------------ | ------------------------------------------------------ | --------------------------------------- | -------------------------------------- | --------------------------------------- |
| NG - Misalign          | 60.00%                                     | 40.00%                                                 | 45.00%                                  | 35.00%                                 | 45.00%                                  |
| NG - No solder         | 70.00%                                     | 80.00%                                                 | 70.00%                                  | 50.00%                                 | 60.00%                                  |
| NG - Not enough solder | 65.00%                                     | 80.00%                                                 | 75.00%                                  | 70.00%                                 | 75.00%                                  |
| NG - Single            | 95.00%                                     | 90.00%                                                 | 90.00%                                  | 100.00%                                | 55.00%                                  |
| OK                     | 75.00%                                     | 75.00%                                                 | 80.00%                                  | 100.00%                                | 80.00%                                  |
| Images                 | [Original Image](../datasets/training_set) | [Generated Image](<../vae/beta-vae/Synthetic\ Images>) | [Generated Image](../sd3.5/inferred/v2) | [Generated Image](../sdxl/inferred/v2) | [Generated Image](../sd1.5/inferred/v3) |

## Binary Classification Accuracy Comparison

### Imbalanced Binary Dataset

_Note: Data imbalanced with OK : NG ratio of 1 : 4_ due to the merging of 4 NG classes into 1

| Class | Original Dataset | SD3.5 + LoRA | SDXL + LoRA |
| ----- | ---------------- | ------------ | ----------- |
| NG    | 95.00%           | 95.00%       | 100.00%     |
| OK    | 80.00%           | 70.00%       | 20.00%      |

### Balanced Binary Dataset

_Note: NG data is selected at random to match the number of OK images_

| Class | Original Dataset | SD3.5 + LoRA | SDXL + LoRA |
| ----- | ---------------- | ------------ | ----------- |
| NG    | 85.00%           | 82.50%       | 100.00%     |
| OK    | 95.00%           | 80.00%       | 45.00%      |

# Extended Set Dataset Results

**Key Differences from Training Set:**

- Contains 100 original OK images (instead of 10) to better represent data imbalance
- 15 generated images added for each NG class (instead of 30), so total NG images = 100, matching OK images

## Multi-Class Classification Accuracy Comparison

| Class                  | Original Dataset                           | SDXL + LoRA                            |
| ---------------------- | ------------------------------------------ | -------------------------------------- |
| NG - Misalign          | 40.00%                                     | 40.00%                                 |
| NG - No solder         | 80.00%                                     | 75.00%                                 |
| NG - Not enough solder | 60.00%                                     | 70.00%                                 |
| NG - Single            | 90.00%                                     | 100.00%                                |
| OK                     | 100.00%                                    | 100.00%                                |
| Images                 | [Original Image](../datasets/extended_set) | [Generated Image](../sdxl/inferred/v4) |

## Binary Classification Accuracy Comparison

| Class | Original Dataset | SDXL + LoRA |
| ----- | ---------------- | ----------- |
| NG    | 93.75%           | 96.25%      |
| OK    | 100.00%          | 90.00%      |
