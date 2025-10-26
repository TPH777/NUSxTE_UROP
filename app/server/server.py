from flask import Flask, request, jsonify
#from model import run_model
app = Flask(__name__)

@app.route("/new_job", methods=["POST"])
def new_job():
  params = request.json['params']
  #run_model(params) #function needs to unpack the hyper-params

@app.route("/test_server", methods=["GET"])
def test_server():
  return jsonify({"test": "test"})

if __name__ == "__main__":
  app.run(port=8000)