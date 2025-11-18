from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from app_backend.train.train import train_model
from app_backend.generate.generate import generate
app = Flask(__name__)
CORS(app)

@app.route("/new_training_job", methods=["POST"])
def new_training_job():
  params = request.json['params']
  name = params['name']
  prompt = params['prompt']
  dataset_path = params['dataset_path']
  batch_size = int(params['batch_size'])
  learning_rate = float(params['learning_rate'])
  epochs = int(params['epochs'])
  resolution = int(params['resolution'])
  memory_efficient = params['memory_efficient']
  train_model(name, prompt, dataset_path, batch_size, learning_rate, epochs, resolution, memory_efficient)
  return jsonify({
      'status': 'success',
      'message': 'Training job started',
  }), 200

@app.route("/new_generate_job", methods=["POST"])
def new_generate_job():
  params = request.json['params']
  name = params['name']
  num_samples = params['num_samples']
  prompt = params['prompt']
  resolution = params['resolution']
  num_inference_steps = params['num_inference_steps']
  guidance_scale = params['guidance_scale']
  generate(name, num_samples, prompt, resolution, num_inference_steps, guidance_scale)
  return jsonify({
      'status': 'success',
      'message': 'Generate job started',
  }), 200

@app.route("/test_server", methods=["GET"])
def test_server():
  return jsonify({"test": "test"})

if __name__ == "__main__":
  app.run(port=8000)