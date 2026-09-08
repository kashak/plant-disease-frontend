"""
Crop Disease Detection API — Phase 7: Combine everything
-----------------------------------------------------------
POST /predict does:

    Receive image
        -> Validate image
        -> Preprocess
        -> AI prediction
        -> Confidence check
        -> Disease lookup
        -> Return JSON

This is the MVP.
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
CONFIDENCE_THRESHOLD = 0.5  # below this, we tell the user we're not sure

# ---------------------------------------------------------
# Startup: load the model and class names ONCE
# ---------------------------------------------------------
print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)

print(f"Model loaded. Classes: {class_names}")


# ---------------------------------------------------------
# Step: Validate image
# ---------------------------------------------------------
def validate_image(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")


# ---------------------------------------------------------
# Step: Preprocess
# ---------------------------------------------------------
def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)  # shape: (1, 224, 224, 3)
    return image_array


# ---------------------------------------------------------
# Step: Disease lookup
# ---------------------------------------------------------
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
        "symptoms": row[3],
        "treatment": row[4],
        "prevention": row[5],
    }


@app.get("/")
def read_root():
    return {"message": "Crop disease API is running"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Step 1: Receive image
    contents = await file.read()

    # Step 2: Validate image
    validate_image(file)
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    # Step 3: Preprocess
    processed = preprocess_image(image)

    # Step 4: AI prediction
    probabilities = model.predict(processed)[0]  # e.g. [0.02, 0.94, 0.03, 0.01]
    predicted_index = int(np.argmax(probabilities))
    predicted_class = class_names[predicted_index]
    confidence = float(probabilities[predicted_index])

    # Step 5: Confidence check
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "disease": predicted_class,
            "confidence": round(confidence, 4),
            "message": (
                "Prediction confidence is low — try a clearer, closer photo of the "
                "affected leaf in good lighting."
            ),
        }

    # Step 6: Disease lookup
    info = get_disease_info(predicted_class)

    # Step 7: Return JSON
    response = {
        "disease": predicted_class,
        "confidence": round(confidence, 4),
    }

    if info:
        response.update(info)
    else:
        response["message"] = "Disease predicted, but no info found in database yet."

    return response
