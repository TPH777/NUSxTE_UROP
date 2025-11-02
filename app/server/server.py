from flask import Flask, request, jsonify
import json
#from app_backend.train import train
#from app_backend.generate import generate
app = Flask(__name__)

@app.route("/new_training_job", methods=["POST"])
def new_training_job():
  params = request.json['params']
  name = params.name
  prompt = params.prompt
  dataset_path = params.dataset_path
  batch_size = int(params.batch_size)
  learning_rate = float(params.learning_rate)
  epochs = int(params.learning_rate)
  resolution = int(params.resolution)
  memory_efficient = json.loads(params.memory_efficient.lower())
#  train(name, prompt, dataset_path, batch_size, learning_rate, epochs, resolution, memory_efficient)

@app.route("/new_generate_job", methods=["POST"])
def new_generate_job():
  params = request.json['params']
  name = params.name
  num_samples = params.num_samples
  prompt = params.prompt
  num_inference_steps = params.num_inference_steps
  guidance_scale = params.guidance_scale
#  generate(name, num_samples, prompt, num_inference_steps, guidance_scale)

@app.route("/test_server", methods=["GET"])
def test_server():
  return jsonify({"test": "test"})

if __name__ == "__main__":
  app.run(port=8000)