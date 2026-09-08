"""
TEMPORARY lite version of main.py
------------------------------------
Use this ONLY to confirm that FastAPI itself starts and responds correctly,
while you're still working on getting the dataset + training the model.

This does NOT load model.keras or class_names.json, so /api/v1/predict
returns fake placeholder data instead of a real prediction.

Once you have model.keras and class_names.json, switch back to the full
main.py version that actually loads and uses them.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Crop Disease Detection API (lite/test mode)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Crop disease API is running (lite/test mode — no model loaded yet)"}


@app.post("/api/v1/predict")
async def predict(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    # No real model yet — just confirming the endpoint receives the file correctly
    return {
        "crop": "Tomato",
        "disease": "Early Blight",
        "confidence": 0.94,
        "description": "Placeholder response — model not loaded yet.",
        "symptoms": ["Dark spots on leaves", "Yellowing around spots"],
        "treatment": ["Apply fungicide", "Remove infected leaves"],
        "prevention": ["Rotate crops", "Avoid overhead watering"],
    }
