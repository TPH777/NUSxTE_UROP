#!/bin/bash
#SBATCH --job-name=qledit
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100-80:1
#SBATCH --time=8:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=100G
#SBATCH --output=ft_qe.out
#SBATCH --error=ft_qe.err

source ~/test/.venv/bin/activate
cd /home/w/weng/test/flymyai-lora-trainer
export ACCELERATE_CONFIG_FILE=/home/w/weng/test/flymyai-lora-trainer/train_configs/train_lora_qwen_edit-2509.yaml

accelerate launch train_qwen_edit_lora.py --config $ACCELERATE_CONFIG_FILE

deactivate
