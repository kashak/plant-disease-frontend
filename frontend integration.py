"""
Crop Disease Detection API — Phase 8: Frontend integration
--------------------------------------------------------------
API CONTRACT (this is what any frontend developer needs to know):

Request:
    POST /api/v1/predict
    Content-Type: multipart/form-data
    Field: image = <leaf.jpg>

Response:
    {
        "crop": "Tomato",
        "disease": "Early Blight",
        "confidence": 0.94,
        "description": "...",
        "symptoms": ["...", "..."],
        "treatment": ["...", "..."],
        "prevention": ["...", "..."]
    }
"""

import json
import sqlite3
import io

import numpy as np
import tensorflow as tf
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Crop Disease Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "crop_diseases.db"
MODEL_PATH = "model.keras"
CLASS_NAMES_PATH = "class_names.json"
IMG_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.5

# ---------------------------------------------------------
# Startup: load the model and class names ONCE
# ---------------------------------------------------------
print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)

print(f"Model loaded. Classes: {class_names}")


def validate_image(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")


def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def to_list(text: str):
    """
    Convert a stored text field into a list of points for the API response,
    e.g. "Apply fungicide. Remove infected leaves." -> ["Apply fungicide.", "Remove infected leaves."]
    Splits on periods; adjust this if you store your DB text differently (e.g. one point per line).
    """
    if not text:
        return []
    parts = [p.strip() for p in text.split(".") if p.strip()]
    return parts


def get_disease_info(disease_name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT crop, disease, description, symptoms, treatment, prevention FROM diseases WHERE disease = ?",
        (disease_name,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "crop": row[0],
        "disease": row[1],
        "description": row[2],
        "symptoms": to_list(row[3]),
        "treatment": to_list(row[4]),
        "prevention": to_list(row[5]),
    }


@app.get("/")
def read_root():
    return {"message": "Crop disease API is running"}


@app.post("/api/v1/predict")
async def predict(image: UploadFile = File(...)):
    # Receive image
    contents = await image.read()

    # Validate image
    validate_image(image)
    try:
        pil_image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    # Preprocess
    processed = preprocess_image(pil_image)

    # AI prediction
    probabilities = model.predict(processed)[0]
    predicted_index = int(np.argmax(probabilities))
    predicted_class = class_names[predicted_index]
    confidence = float(probabilities[predicted_index])

    # Confidence check
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "disease": predicted_class,
            "confidence": round(confidence, 4),
            "message": (
                "Prediction confidence is low — try a clearer, closer photo of the "
                "affected leaf in good lighting."
            ),
        }

    # Disease lookup
    info = get_disease_info(predicted_class)

    # Return JSON matching the contract
    response = {
        "disease": predicted_class,
        "confidence": round(confidence, 4),
    }

    if info:
        response.update(info)
    else:
        response["message"] = "Disease predicted, but no info found in database yet."

    return response
