from flask import Flask, request, Response
from flask_cors import CORS
import sys, os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.Model import process_image_json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.after_request
def add_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return Response("No file uploaded", status=400, mimetype="text/plain")

    img_file = request.files["file"]
    img_path = os.path.join(UPLOAD_FOLDER, img_file.filename)
    img_file.save(img_path)

    # Run model
    result = process_image_json(img_path)

    # Convert result dict to readable text
    output_lines = []
    for key, value in result.items():
        output_lines.append(f"{key}: {value}")
    output_text = "\n".join(output_lines)

    return Response(output_text, mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)
