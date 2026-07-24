from database import create_database, save_prediction
from report_generator import generate_medical_report
from flask import Flask, request, jsonify, send_from_directory
from database import get_history

import tensorflow as tf
import numpy as np
import cv2
import os

from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input

app = Flask(__name__)
create_database()


# Folders
UPLOAD_FOLDER = "uploads"
GRADCAM_FOLDER = "gradcam_results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRADCAM_FOLDER, exist_ok=True)


# Load Model
print("Loading model...")
model = load_model("medical_model.keras")
print("Model loaded successfully!")


# Home Route
@app.route("/")
def home():
    return {
        "project": "Advanced AI Medical Intelligence Platform",
        "status": "Running",
        "model": "Medical Model Loaded Successfully"
    }

@app.route("/gradcam/<filename>")
def serve_gradcam(filename):

    return send_from_directory(
        GRADCAM_FOLDER,
        filename
    )

# Image Preprocessing
def preprocess_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Unable to read image.")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    return img


# Prediction
def predict_image(image_path):

    img = preprocess_image(image_path)

    prediction = model.predict(img, verbose=0)[0][0]

    if prediction > 0.5:
        disease = "PNEUMONIA"
        confidence = float(prediction * 100)
    else:
        disease = "NORMAL"
        confidence = float((1 - prediction) * 100)

    return disease, confidence

def generate_gradcam(image_path, output_path):

    # Read image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    original_img = img.copy()

    # Resize
    img = cv2.resize(img, (224, 224))

    img_array = np.expand_dims(img, axis=0)
    img_array = preprocess_input(img_array)

    # Build GradCAM model
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[
            model.get_layer("top_activation").output,
            model.output
        ]
    )

    # Compute gradients
    with tf.GradientTape() as tape:

        conv_outputs, predictions = grad_model(img_array)

        loss = predictions[:, 0]

    grads = tape.gradient(loss, conv_outputs)

    pooled_grads = tf.reduce_mean(
        grads,
        axis=(0, 1, 2)
    )

    conv_outputs = conv_outputs[0]

    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]

    heatmap = tf.squeeze(heatmap)

    heatmap = tf.maximum(heatmap, 0)

    heatmap /= tf.math.reduce_max(heatmap)

    heatmap = heatmap.numpy()

    # Resize heatmap
    heatmap = cv2.resize(
        heatmap,
        (
            original_img.shape[1],
            original_img.shape[0]
        )
    )

    # Convert to RGB heatmap
    heatmap = np.uint8(255 * heatmap)

    heatmap = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    heatmap = cv2.cvtColor(
        heatmap,
        cv2.COLOR_BGR2RGB
    )

    # Overlay
    overlay = cv2.addWeighted(
        original_img,
        0.6,
        heatmap,
        0.4,
        0
    )

    # Save
    cv2.imwrite(
        output_path,
        cv2.cvtColor(
            overlay,
            cv2.COLOR_RGB2BGR
        )
    )

    return output_path


# Prediction API
@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image uploaded."
        }), 400

    file = request.files["image"]

    image_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(image_path)

    disease, confidence = predict_image(image_path)

    report = generate_medical_report(
    disease,
    confidence
)

    filename = os.path.splitext(file.filename)[0]

    gradcam_filename = f"{filename}_gradcam.png"

    gradcam_path = os.path.join(
        GRADCAM_FOLDER,
        gradcam_filename
    )

    generate_gradcam(
    image_path,
    gradcam_path
)
    save_prediction(
    filename=file.filename,
    prediction=disease,
    confidence=round(confidence, 2),
    gradcam_path=gradcam_path,
    medical_report=report
)

    return jsonify({
        "success": True,
        "filename": file.filename,
        "prediction": disease,
        "confidence": round(confidence, 2),
        "gradcam_image": f"http://127.0.0.1:5000/gradcam/{gradcam_filename}",
        "medical_report": report
    })

# History API
@app.route("/history", methods=["GET"])
def history():
    history = get_history()
    return jsonify(history)

# Run App
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)