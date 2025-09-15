#!/bin/bash
#SBATCH --job-name=sd3.5-infer
#SBATCH --partition=gpu
#SBATCH --gres=gpu:h100-47:1
#SBATCH --time=0:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --output=ft.out
#SBATCH --error=ft.err

source /home/t/tph777/sd3/bin/activate
cd /home/t/tph777/sd3.5
python3 infer.py

deactivate
