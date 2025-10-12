#!/bin/bash
#SBATCH --job-name=classification
#SBATCH --partition=gpu
#SBATCH --gres=gpu:h100-47:1
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --output=ft.out
#SBATCH --error=ft.err

export TRAIN_DIR="/home/t/tph777/extended_set/newprompt_ds/train"
export VALID_DIR="/home/t/tph777/extended_set/newprompt_ds/valid"
export TEST_DIR="/home/t/tph777/extended_set/newprompt_ds/test"

source /home/t/tph777/sd3/bin/activate
cd /home/t/tph777/classification
python3 train.py --train_dir "$TRAIN_DIR" --valid_dir "$VALID_DIR"
python3 test.py --test_dir "$TEST_DIR"

deactivate
