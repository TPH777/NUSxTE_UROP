#!/bin/bash
#SBATCH --job-name=sd3.5-finetune
#SBATCH --partition=gpu
#SBATCH --gres=gpu:h100-47:1
#SBATCH --time=0:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=40G
#SBATCH --output=ft.out
#SBATCH --error=ft.err

source ~/sd3/bin/activate

export ACCELERATE_CONFIG_FILE="/home/t/tph777/.cache/huggingface/accelerate/default_config.yaml"

export VERSION="v2"
export VALIDATION_PROMPT="NG - Single"
export TRAIN_DIR="/home/t/tph777/training_set/train/$VALIDATION_PROMPT"
export OUTPUT_DIR="/home/t/tph777/sd3.5/output/$VERSION/$VALIDATION_PROMPT"

accelerate launch --config_file $ACCELERATE_CONFIG_FILE ~/diffusers/examples/dreambooth/train_dreambooth_lora_sd3.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-3-medium-diffusers"  \
  --instance_data_dir="$TRAIN_DIR" \
  --output_dir=$OUTPUT_DIR \
  --mixed_precision="bf16" \
  --instance_prompt="$VALIDATION_PROMPT" \
  --resolution=256 \
  --train_batch_size=1 \
  --num_train_epochs=2 --checkpointing_steps=500 \
  --max_train_steps=2000 \
  --gradient_accumulation_steps=1 \
  --learning_rate=4e-4 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --rank=16 \
  --seed="0" \
  --validation_prompt="$VALIDATION_PROMPT" \