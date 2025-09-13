#!/bin/bash
#SBATCH --job-name=sdxl-finetune
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100-80:1
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --output=ft.out
#SBATCH --error=ft.err

# source ~/sdxl/bin/activate
# python ~/diffusers/examples/text_to_image/infer.py
# deactivate

source ~/sdxl/bin/activate
cd /home/t/tph777/diffusers/examples/text_to_image
python infer.py
deactivate
