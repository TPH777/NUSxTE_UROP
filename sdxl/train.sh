#!/bin/bash
#SBATCH --job-name=sdxl-finetune
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100-80:1
#SBATCH --time=8:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=20G
#SBATCH --output=ft.out
#SBATCH --error=ft.err

export MODEL_NAME="stabilityai/stable-diffusion-xl-base-1.0"
export VAE_NAME="madebyollin/sdxl-vae-fp16-fix"
export ACCELERATE_CONFIG_FILE="/home/t/tph777/.cache/huggingface/accelerate/default_config.yaml"

export TRAIN_DIR="./dataset1"
export VALIDATION_PROMPT="NG - Not enough solder"
export OUTPUT_DIR="./output/sdxl-finetuned3"

source ~/sdxl/bin/activate
cd /home/t/tph777/diffusers/examples/text_to_image

accelerate launch --config_file $ACCELERATE_CONFIG_FILE train_text_to_image_lora_sdxl.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --pretrained_vae_model_name_or_path=$VAE_NAME \
  --train_data_dir=$TRAIN_DIR \
  --enable_xformers_memory_efficient_attention \
  --resolution=384 --random_flip \
  --train_batch_size=1 \
  --num_train_epochs=2 --checkpointing_steps=500 \
  --max_train_steps=6500 \
  --learning_rate=1e-04 --lr_scheduler="constant" --lr_warmup_steps=0 \
  --mixed_precision="fp16" \
  --seed=42 \
  --train_text_encoder \
  --validation_prompt="$VALIDATION_PROMPT" --report_to="wandb"\
  --output_dir=${OUTPUT_DIR}

deactivate
