#!/bin/bash
#SBATCH --job-name=qe_infer
#SBATCH --partition=gpu
#SBATCH --gres=gpu:h100-96:1
#SBATCH --time=0:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=200G
#SBATCH --output=ft_qei.out
#SBATCH --error=ft_qei.err

source /home/w/weng/test/.venv/bin/activate
cd /home/w/weng/test/flymyai-lora-trainer
export ACCELERATE_CONFIG_FILE=/home/w/weng/test/flymyai-lora-trainer/train_configs/train_lora_qwen_edit.yaml

python3 qwen_image_edit_inference.py

deactivate
