# Synthetic Image Toolkit

This repository contains a toolkit for generating synthetic images using SDXL, by training LoRA adapters, running inference/generation, and evaluating generated images for downstream classification tasks.

This README consolidates the project's layout, purpose of important files/folders, and quick run instructions.

**Prerequisites**

- Python 3.10+ (use a virtual environment)
- If using GPU: CUDA-enabled machine, appropriate `torch`/`cuda` install

**Quick start**

1. Create and activate a virtual environment.
   - Windows (PowerShell): `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
2. Install requirements for the backend (example):

   - `pip install -r app/server/app_backend/requirements.txt`

3. Running the Electron UI (renderer + server)

   - The repository includes a desktop Electron wrapper in `app/` that runs the React renderer, an Electron process and the Python server together using `npm start`.
   - To run the app (PowerShell):

     ```powershell
     cd app
     npm install
     cd renderer
     npm install
     cd ..
     npm start
     ```

Project layout (high level)

- `app/` — UI and server glue. Contains a renderer (React/Vite) and `server/` which exposes HTTP endpoints to start training / generation.

  - `app/server/server.py` — Flask app exposing endpoints:
    - `POST /new_training_job` — start training (calls `app_backend.train.train.train_model`)
    - `POST /new_generate_job` — start generation (calls `app_backend.generate.generate.generate`)
  - `app/server/app_backend/` — core Python backend modules for training, generation and evaluation
    - `train/` — training wrapper and helper scripts
      - `train.py` — `train_model(...)` function. It: generates `metadata.jsonl` (via `utilities/metadata.py`), builds an `accelerate launch` command and spawns a subprocess that runs `train_text_to_image_lora_sdxl.py`.
      - `data_prep.py` — helper(s) for preparing datasets (see file for details).
      - `accelerate_config.yaml` — accelerate configuration used by `accelerate launch`.
    - `generate/` — generation pipeline
      - `generate.py` — `generate(...)` function. Loads a Diffusers pipeline, loads LoRA weights from the training output folder and writes generated PNGs to `output/`.
    - `evaluate/` — evaluation utilities
      - `evaluate.py` — orchestrates evaluation (Inception Score, FID, LPIPS) and writes a `metrics.json` plus logs.

- `datasets/` — datasets used for training / validation / testing. Several dataset variants are present (`training_set`, `extended_set`, `new_set_with_vae`, etc.). Each class typically lives in a subfolder used as the prompt token when generating `metadata.jsonl`.
- `vae/` — VAE-based synthetic generation scripts (examples for conditional VAE generation, synthetic pipelines used in experiments).
- `sd3.5/`, `sd1.5/`, `sdxl/` — experiment scripts for different Stable Diffusion model variants. Useful utilities and `infer.py` show how LoRA weights are loaded and inference is performed in batch.
- `classification/` — classification experiments and methodology notes (contains a `README.md` with evaluation tables and methodology used in the project).
- `evaluation/` — other metric helpers (scripts computing FID, IS, LPIPS, etc.).
- `utilities/` — small helper scripts
  - `metadata.py` — convenience function `generate_metadata_jsonl(root_dir)` that walks a dataset folder and creates `metadata.jsonl` in the dataset root. Important for Hugging Face Diffusers training.

Important files to know

- `app/server/server.py` — starts a Flask service to accept training/generation jobs via JSON POSTs.
- `app/server/app_backend/train/train.py` — `train_model(...)` entrypoint used by the server. Uses `accelerate launch` to run the actual training script `train_text_to_image_lora_sdxl.py` and streams logs into `train.log`.
- `app/server/app_backend/generate/generate.py` — `generate(...)` entrypoint used by the server. Loads a pipeline from `stabilityai/stable-diffusion-xl-base-1.0`, applies the LoRA weights found in the training output folder and writes images to `app/server/app_backend/generate/output/`.
- `utilities/metadata.py` — generates `metadata.jsonl` (file list with text labels) used by Diffusers training.

How to run training (two options)

1. Run via Flask server API (recommended for the toolkit UI):

   - Start the server: `python app/server/server.py` (defaults to port 8000).
   - POST JSON to `http://localhost:8000/new_training_job` with body like:
     {
     "params": {
     "name": "experiment-name",
     "prompt": "My Prompt Token",
     "dataset_path": "path/to/dataset/root",
     "batch_size": 4,
     "learning_rate": 1e-4,
     "epochs": 10,
     "resolution": 512,
     "memory_efficient": false
     }
     }

   The server will call `train_model(...)` which generates `metadata.jsonl` and runs `accelerate launch` against `train_text_to_image_lora_sdxl.py`. Logs are written to `app/server/app_backend/train/train.log` and a copy is placed under the experiment's output folder.

2. Run training directly (for debugging / iterative development):
   - Prepare `metadata.jsonl` in your dataset root: `python utilities/metadata.py path/to/dataset` (or call `generate_metadata_jsonl` programmatically).
   - Inspect `train/train_text_to_image_lora_sdxl.py` for training arguments and run using `accelerate launch --config_file app/server/app_backend/train/accelerate_config.yaml app/server/app_backend/train/train_text_to_image_lora_sdxl.py --train_data_dir=...` (see `train.py` for the exact flags used).

How to generate images

1. Via Flask server API:

   - POST JSON to `http://localhost:8000/new_generate_job` with body like:
     {
     "params": {
     "name": "experiment-name",
     "num_samples": 10,
     "prompt": "My Prompt Token",
     "resolution": 512,
     "num_inference_steps": 50,
     "guidance_scale": 7.5
     }
     }

   The server calls `generate(...)`, which looks for LoRA weights under the matching training output folder and writes images into `app/server/app_backend/generate/output/<name>/<prompt>/`.

2. Run the generation script directly:
   - Inspect `app/server/app_backend/generate/generate.py` and run it as a module or call the function from a small wrapper script. Ensure you have the trained LoRA weights available as `pytorch_lora_weights.safetensors` in the training output folder.

Evaluation

- The evaluation pipeline lives in `app/server/app_backend/evaluate/`. `evaluate.py` orchestrates Inception Score, FID (overall and per-class) and LPIPS metrics, writing results to `output/<name>/metrics.json` and an `evaluate.log` file.

Notes, tips and gotchas

- GPU / CUDA: training and generation expect GPU for reasonable performance. The project requirements pin specific `torch` and CUDA-compatible packages — adjust to your environment if necessary.
- Accelerate: training uses `accelerate launch` and an included `accelerate_config.yaml`. Ensure `accelerate` is configured for your hardware (e.g. `accelerate config` interactive setup can help).
- Metadata: `utilities/metadata.py` is a simple but important helper to prepare the dataset metadata used by the Diffusers training loop. It assumes class-folder names in the dataset are the text prompts.
- Logs: Training/generation/evaluation create logs under their respective module directories and copy a backup to the output experiment folder. Inspect these logs for runtime errors.
- Model & LoRA weights: training output is placed under `app/server/app_backend/train/output/<name>/<prompt>/`. The generation code expects `pytorch_lora_weights.safetensors` to be present in that folder.

Further exploration

- `classification/README.md` — contains experiment results, methodology and numeric comparisons from the project experiments.
- `app/renderer/` — the frontend. To run the UI, inspect its `package.json` and use `npm/yarn` in that folder (React + Vite + TypeScript).
- `vae/` — VAE-based synthetic generation scripts and examples used by the paper implementation.

If you'd like, I can:

- Add example API `curl` commands or a minimal Postman collection for the server endpoints.
- Detect and add missing `requirements.txt` files for other subfolders (renderer, vae) and create a single `requirements.txt` at the repo root.

---

Generated automatically by repository inspection on request. If you want any section expanded (examples, `curl` snippets, or step-by-step GPU setup), tell me which part to expand.
