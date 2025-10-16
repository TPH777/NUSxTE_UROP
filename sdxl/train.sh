#!/bin/bash
#SBATCH --job-name=sdxl-finetune
#SBATCH --partition=gpu
#SBATCH --gres=gpu:h100-47:1
#SBATCH --time=8:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=20G
#SBATCH --output=ft.out
#SBATCH --error=ft.err

export MODEL_NAME="stabilityai/stable-diffusion-xl-base-1.0"
export VAE_NAME="madebyollin/sdxl-vae-fp16-fix"
export ACCELERATE_CONFIG_FILE="/home/t/tph777/.cache/huggingface/accelerate/default_config.yaml"

export VERSION="v6"
export RESOLUTION=512
export NUM_SAMPLES=15
export TRAIN_DIR="/home/t/tph777/extended_set/newprompt_ds/train"
export VALIDATION_PROMPT="<CLS_NG> images with pins misaligned, but no pin missing and all pins fully soldered."
export OUTPUT_DIR="/home/t/tph777/sdxl/output/$VERSION"

source ~/sdxl/bin/activate 

# Training
accelerate launch --config_file $ACCELERATE_CONFIG_FILE /home/t/tph777/diffusers/examples/text_to_image/train_text_to_image_lora_sdxl.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --pretrained_vae_model_name_or_path=$VAE_NAME \
  --train_data_dir=$TRAIN_DIR \
  --resolution=$RESOLUTION \
  --random_flip \
  --train_batch_size=1 \
  --num_train_epochs=2 --checkpointing_steps=500 \
  --max_train_steps=6500 \
  --learning_rate=1e-04 --lr_scheduler="constant" --lr_warmup_steps=0 \
  --mixed_precision="fp16" \
  --seed=42 \
  --train_text_encoder \
  --validation_prompt="$VALIDATION_PROMPT" \
  --output_dir=${OUTPUT_DIR} \
  --enable_xformers_memory_efficient_attention \
  # --report_to="wandb" \

# Inference
python3 /home/t/tph777/sdxl/infer.py --version $VERSION --num_samples $NUM_SAMPLES --resolution $RESOLUTION

deactivate
