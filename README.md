# Synthetic Image Toolkit

This repository provides a toolkit for generating synthetic images (SDXL) by training LoRA adapters, running generation/inference, and evaluating the outputs for downstream classification tasks.

This README gives a concise overview, quick start instructions, and pointers to the most important files and folders in the project.

**Prerequisites**

- Python 3.10+ (use a virtual environment)
- If using GPU: CUDA-enabled machine, compatible `torch`/CUDA install, and sufficient VRAM (experiments here typically assume >=24GB VRAM). NOTE: GPU training has not been extensively tested in this project due to limited access to GPU hardware (see the "Hardware & Testing" note below).

**Quick start**

1. Clone the repository and change into it.

   - PowerShell: `git clone https://github.com/TPH777/NUSxTE_UROP.git; cd NUSxTE_UROP`

2. Create and activate a virtual environment.

   - Windows (PowerShell): `python -m venv .venv; .\.venv\Scripts\Activate.ps1`

3. Install backend requirements (example):

   - `pip install -r app/server/app_backend/requirements.txt`

4. Run the Electron UI (renderer + server)

   - The `app/` folder contains an Electron wrapper that runs the React renderer and the Python server together. To run the UI (PowerShell):

     ```powershell
     cd app
     npm install
     cd renderer
     npm install
     cd ..
     npm start
     ```

5. Start training and generating: [UI Demo Video](./Demo%20video.mp4)

**Project layout (high level)**

- `app/` — UI and server glue. Contains a renderer (React/Vite) and a `server/` that exposes HTTP endpoints used by the UI to start training and generation jobs.

  - `app/server/server.py` — Flask app exposing endpoints:

    - `POST /new_training_job` — starts training (calls `app_backend.train.train.train_model`).
    - `POST /new_generate_job` — starts generation (calls `app_backend.generate.generate.generate`).

  - `app/server/app_backend/` — core Python backend modules for training, generation and evaluation.

    - `train/` — training wrappers and helpers

      - `train.py` — `train_model(...)` generates `metadata.jsonl` (via `utilities/metadata.py`), builds an `accelerate launch` command, and spawns the training subprocess (`train_text_to_image_lora_sdxl.py`).
      - `data_prep.py` — helpers for preparing datasets.
      - `accelerate_config.yaml` — accelerate configuration used by `accelerate launch` (set `use_cpu: false` for GPU runs).

    - `generate/` — generation pipeline

      - `generate.py` — `generate(...)` loads a Diffusers pipeline, applies LoRA weights from training outputs, and writes generated PNGs to `output/`.

    - `evaluate/` — evaluation utilities
      - `evaluate.py` — orchestrates evaluation (Inception Score, FID, LPIPS), writes a `metrics.json`, and generates logs. (Currently not integrated into the UI.)

Experimental scripts (independent of the toolkit):

- `datasets/` — datasets used for training / validation / testing. Several dataset variants are present (`training_set`, `extended_set`, `new_set_with_vae`, etc.). Each class typically lives in a subfolder used as the prompt token when generating `metadata.jsonl`.
- `vae/`, `sd3.5/`, `sd1.5/`, `sdxl/` — experiment scripts for different generative model variants.
- `classification/` — classification experiments and methodology notes (contains a `README.md` with evaluation tables and methodology used in the project).
- `evaluation/` — other metric helpers (scripts computing FID, IS, LPIPS, etc.).
- `utilities/` — small helper scripts
  - `metadata.py` — convenience function `generate_metadata_jsonl(root_dir)` that walks a dataset folder and creates `metadata.jsonl` in the dataset root. Important for Hugging Face Diffusers training.
