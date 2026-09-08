from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Crop disease API is running"}
"""
Crop Disease Detection API
---------------------------
A simple FastAPI backend that:
1. Accepts an uploaded photo of a crop leaf
2. Predicts the disease (currently a placeholder — swap in your trained model later)
3. Looks up the cure/prevention info from the SQLite database
4. Returns everything as JSON for your frontend/website to display
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import sqlite3

app = FastAPI(title="Crop Disease Detection API")

# Allow your future website (running on a different port/domain) to call this API.
# For development this allows all origins — tighten this before going live.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "crop_diseases.db"


def get_disease_info(disease_name: str):
    """Fetch symptoms/cure/prevention for a disease name from the SQLite database."""
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


def predict_disease(image: Image.Image) -> str:
    """
    PLACEHOLDER prediction function.

    Right now this always returns the same disease name so you can test
    the full pipeline (upload -> predict -> DB lookup -> response) end to end
    BEFORE your real model is trained.

    Once train_model.py produces a trained model, replace the body of this
    function with something like:

        import numpy as np
        import tensorflow as tf

        model = tf.keras.models.load_model("crop_disease_model.h5")
        class_names = ["Early Blight", "Late Blight", "Healthy", ...]  # match training order

        img = image.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        predicted_class = class_names[np.argmax(predictions)]
        return predicted_class

    For now, it just returns a fixed label so you can test everything else works.
    """
    return "Early Blight"


@app.get("/")
def read_root():
    return {"message": "Crop disease API is running"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Basic validation — only accept image files
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    # Read the uploaded file into a PIL image
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    # Run prediction (placeholder for now, real model later)
    disease_name = predict_disease(image)

    # Look up cure/prevention info from the database
    info = get_disease_info(disease_name)

    if info is None:
        return {
            "disease_name": disease_name,
            "message": "Disease predicted, but no cure info found in database yet.",
        }

    return info

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import sqlite3

app = FastAPI(title="Crop Disease Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    disease_name = "Early Blight"  # placeholder until real model is trained

    return {
        "crop": "Tomato",
        "disease_name": disease_name,
        "symptoms": "Dark concentric spots on older leaves",
        "cure": "Apply copper-based fungicide; remove infected leaves",
        "prevention": "Rotate crops; avoid overhead watering"
    }
##there have to connect frontend

from PIL import Image
import numpy as np

def preprocess_image(image_path, target_size=(224, 224)):
    # Step 1: Open the image
    image = Image.open(image_path)

    # Step 2: Convert to RGB (handles cases where image is grayscale or has an alpha channel)
    image = image.convert("RGB")

    # Step 3: Resize to the target size (224x224 is what MobileNetV2 expects)
    image = image.resize(target_size)

    # Step 4: Convert to a numpy array
    image_array = np.array(image)

    # Step 5: Normalize pixel values from [0, 255] to [0, 1]
    normalized_array = image_array / 255.0

    return normalized_array


# Example usage
if __name__ == "__main__":
    result = preprocess_image("test_leaf.jpg")
    print("Shape:", result.shape)        # Should print: (224, 224, 3)
    print("Min value:", result.min())    # Should be 0.0
    print("Max value:", result.max())    # Should be close to 1.0
    """
Phase 4 — Train AI
-------------------
Trains a crop disease classifier using transfer learning on MobileNetV2.

INPUT expected:
    A folder called "dataset" in your project root, structured like:

    dataset/
        Tomato___Early_blight/
            img1.jpg
            img2.jpg
        Tomato___Late_blight/
            img1.jpg
        Tomato___healthy/
            img1.jpg
        ...

OUTPUT produced:
    model.keras        <- the trained model
    class_names.json    <- list of class names, in the order the model uses them
"""
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