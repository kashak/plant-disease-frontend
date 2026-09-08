"""
Crop Disease Detection API — Phase 5
--------------------------------------
Startup:  Load model.keras once when the server starts (not on every request — that would be slow)
User flow: POST /predict -> image -> preprocess -> model.predict() -> probabilities -> highest probability -> disease name -> DB lookup -> JSON response
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

# ---------------------------------------------------------
# Startup: load the model and class names ONCE, when the
# server starts — not on every request, since loading a
# model is slow and doesn't need to be repeated.
# ---------------------------------------------------------
print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)

print(f"Model loaded. Classes: {class_names}")


def preprocess_image(image: Image.Image) -> np.ndarray:
    """Resize, convert to array, normalize, and add the batch dimension the model expects."""
    image = image.convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)  # shape: (1, 224, 224, 3)
    return image_array


def get_disease_info(disease_name: str):
    """Look up symptoms/cure/prevention from the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT crop, disease_name, symptoms, cure, prevention FROM diseases WHERE disease_name = ?",
        (disease_name,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "crop": row[0],
        "disease_name": row[1],
        "symptoms": row[2],
        "cure": row[3],
        "prevention": row[4],
    }


@app.get("/")
def read_root():
    return {"message": "Crop disease API is running"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    # image -> preprocess
    processed = preprocess_image(image)

    # model.predict() -> probabilities
    probabilities = model.predict(processed)[0]  # e.g. [0.02, 0.94, 0.03, 0.01]

    # highest probability -> predicted class
    predicted_index = int(np.argmax(probabilities))
    predicted_class = class_names[predicted_index]
    confidence = float(probabilities[predicted_index])

    # look up cure/prevention info from the database
    info = get_disease_info(predicted_class)

    response = {
        "disease_name": predicted_class,
        "confidence": round(confidence, 4),
    }

    if info:
        response.update(info)
    else:
        response["message"] = "Disease predicted, but no cure info found in database yet."

    return response
