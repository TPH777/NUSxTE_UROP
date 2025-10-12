# Classification Methodology

# Methodology

1. **Initial dataset:** 10 training images, 20 testing images for each class
2. **Baseline:** Train classification model with the 10 training images and test with the 20 to get baseline accuracy
3. **Generation:** Train generative model with the initial dataset training images (10) to produce 30 additional images for each class
4. **Retraining:** Retrain classification model with 10+30=40 training images
5. **Evaluation:** Test the new model with the same 20 images and compare with baseline accuracy

---

# V1. Training Set Dataset Results

## Multi-Class Classification Accuracy Comparison

| Class                  | Original Dataset                           | VAE Model                                             | SD3.5 + LoRA                            | SDXL + LoRA                            | SD1.5 + LORA                            |
| ---------------------- | ------------------------------------------ | ----------------------------------------------------- | --------------------------------------- | -------------------------------------- | --------------------------------------- |
| NG - Misalign          | 60.00%                                     | 40.00%                                                | 45.00%                                  | 35.00%                                 | 45.00%                                  |
| NG - No solder         | 70.00%                                     | 80.00%                                                | 70.00%                                  | 50.00%                                 | 60.00%                                  |
| NG - Not enough solder | 65.00%                                     | 80.00%                                                | 75.00%                                  | 70.00%                                 | 75.00%                                  |
| NG - Single            | 95.00%                                     | 90.00%                                                | 90.00%                                  | 100.00%                                | 55.00%                                  |
| OK                     | 75.00%                                     | 75.00%                                                | 80.00%                                  | 100.00%                                | 80.00%                                  |
| Images                 | [Original Image](../datasets/training_set) | [Generated Image](../vae/beta-vae/Synthetic%20Images) | [Generated Image](../sd3.5/inferred/v2) | [Generated Image](../sdxl/inferred/v2) | [Generated Image](../sd1.5/inferred/v3) |

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

# V2. Extended Set Dataset Results

**Key Differences from Training Set:**

- Contains 100 original OK images (instead of 10) to better represent data imbalance
- 15 generated images added for each NG class (instead of 30), so total NG images = 100, matching OK images

## Multi-Class Classification Accuracy Comparison

- 20 test images for each class

| Class                  | Original Dataset                           | SDXL + LoRA                            |
| ---------------------- | ------------------------------------------ | -------------------------------------- |
| NG - Misalign          | 60.00%                                     | 45.00%                                 |
| NG - No solder         | 70.00%                                     | 90.00%                                 |
| NG - Not enough solder | 55.00%                                     | 25.00%                                 |
| NG - Single            | 95.00%                                     | 90.00%                                 |
| OK                     | 100.00%                                    | 100.00%                                |
| Images                 | [Original Image](../datasets/extended_set) | [Generated Image](../sdxl/inferred/v4) |

#### Original Dataset Confusion Matrix

| Predicted →<br>Actual ↓ | Misalign | No Solder | Not Enough | Single | OK  |
| ----------------------- | -------- | --------- | ---------- | ------ | --- |
| **Misalign**            | 12       | 3         | 1          | 1      | 3   |
| **No Solder**           | 4        | 14        | 0          | 1      | 1   |
| **Not Enough**          | 5        | 0         | 11         | 0      | 4   |
| **Single**              | 0        | 1         | 0          | 19     | 0   |
| **OK**                  | 0        | 0         | 0          | 0      | 20  |

#### SDXL + LoRA Confusion Matrix

| Predicted →<br>Actual ↓ | Misalign | No Solder | Not Enough | Single | OK  |
| ----------------------- | -------- | --------- | ---------- | ------ | --- |
| **Misalign**            | 8        | 5         | 3          | 1      | 3   |
| **No Solder**           | 1        | 18        | 0          | 1      | 0   |
| **Not Enough**          | 5        | 1         | 5          | 0      | 9   |
| **Single**              | 0        | 1         | 0          | 19     | 0   |
| **OK**                  | 0        | 0         | 0          | 0      | 20  |

## Binary Classification Accuracy Comparison

- 20 OK and 80 NG test images.

| Class | Original Dataset | SDXL + LoRA |
| ----- | ---------------- | ----------- |
| NG    | 95.00%           | 93.75%      |
| OK    | 85.00%           | 95.00%      |

#### Original Dataset Confusion Matrix

| Predicted →<br>Actual ↓ |  NG |  OK |
| ----------------------- | --: | --: |
| NG                      |  76 |   4 |
| OK                      |   3 |  17 |

- Notes: Misclassified NG images come from multiple NG subclasses (all except 'Single').

#### SDXL + LoRA Confusion Matrix

| Predicted →<br>Actual ↓ |  NG |  OK |
| ----------------------- | --: | --: |
| NG                      |  75 |   5 |
| OK                      |   1 |  19 |

- Notes: Misclassified NG images are all from the 'Not enough solder' subclass.

# V2.1 Extended Set With Updated Prompt Results

**Key Differences:**

- Split 20 test images into 5 valid images and 15 test images, so that the training model weights is chosen based on the epochs that provide the greatest validation accuracy, separate from test datasets to prevent overfitting and improve generalisability.
- Prompt is change to more natural language:
  mapping = {
  "NG - Misalign": "<CLS_Misaligned_Pins> images with pins misaligned, but no pin missing and all pins fully soldered.",
  "NG - No solder": "<CLS_No_Solder> images with pins without any solder, but all pins present and aligned.",
  "NG - Not enough solder": "<CLS_Low_Solder> images with pins that have reduced solder, but all pins present and aligned.",
  "NG - Single": "<CLS_Single_Sided_Pin> images with only one side of a pin visible, and all visible pins aligned and fully soldered.",
  "OK": "<CLS_OK> images with pins perfectly aligned and fully soldered."
  }

## Multi-Class Classification Accuracy Comparison

- 15 test images for each class

| Class                  | Original                                   | SDXL + LoRA (Old prompt) | SDXL + LoRA (New prompt)               |
| ---------------------- | ------------------------------------------ | ------------------------ | -------------------------------------- |
| <CLS_Low_Solder>       | 73.33%                                     | 46.67%                   | 33.33%                                 |
| <CLS_Misaligned_Pins>  | 33.33%                                     | 20.00%                   | 66.67%                                 |
| <CLS_No_Solder>        | 60.00%                                     | 86.67%                   | 73.33%                                 |
| <CLS_OK>               | 93.33%                                     | 93.33%                   | 100.00%                                |
| <CLS_Single_Sided_Pin> | 93.33%                                     | 80.00%                   | 73.33%                                 |
| Images                 | [Original Image](../datasets/extended_set) |                          | [Generated Image](../sdxl/inferred/v5) |
| Inception Score        | -                                          | 2.72                     | 2.56                                   |
| FID (Multi) Score      | -                                          | 146.38                   | 138.20                                 |

- Notes:

  - Inception score may not be a good indicator as it uses an ImageNet-trained InceptionV3 classifier, so values can be misleading for domain-specific images and should be interpreted cautiously.
    - The higher the better.
  - In contrast, FID compares the distribution of features (extracted by InceptionV3) between real and generated datasets, irrespective of its labels.
  - FID (multi-class) score measures how well the overall distribution of generated features matches the real data across all classes.

- FID (Single Class)

| Class                  | SDXL + LoRA (Old prompt) | SDXL + LoRA (New prompt) |
| ---------------------- | ------------------------ | ------------------------ |
| <CLS_Low_Solder>       | 242.36                   | 234.97                   |
| <CLS_Misaligned_Pins>  | 224.65                   | 233.76                   |
| <CLS_No_Solder>        | 195.56                   | 179.65                   |
| <CLS_OK>               | 177.55                   | 176.10                   |
| <CLS_Single_Sided_Pin> | 168.57                   | 141.14                   |

- Notes: FID (single-class) score can be more informative for targeted defect generation because it measures how closely generated images match each real class individually.
  - The lower the better.
