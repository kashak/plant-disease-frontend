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

import json
import tensorflow as tf
layers = tf.keras.layers
models = tf.keras.models
import json
MobileNetV2 = tf.keras.applications.MobileNetV2
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)

# ---------------------------
# Settings
# ---------------------------
DATASET_DIR ="dataset"
IMG_SIZE = (224, 224)         # MobileNetV2's expected input size
BATCH_SIZE = 32
EPOCHS = 10                   # increase later once you confirm this runs correctly

# ---------------------------
# Step 1: Load the dataset from folders
# ---------------------------
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)

class_names = train_ds.class_names
print("Classes found:", class_names)

# ---------------------------
# Step 2: Save class names to JSON (needed later by the API to decode predictions)
# ---------------------------
with open("class_names.json", "w") as f:
    json.dump(class_names, f)

print("Saved class_names.json")

# ---------------------------
# Step 3: Improve performance with caching/prefetching
# ---------------------------
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# ---------------------------
# Step 4: Build the model using MobileNetV2 as the base (transfer learning)
# ---------------------------
base_model = MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,       # exclude MobileNetV2's original classification head
    weights="imagenet",
)
base_model.trainable = False  # freeze the pretrained layers so we only train our new ones

num_classes = len(class_names)

model = models.Sequential([
    layers.Rescaling(1.0 / 255, input_shape=IMG_SIZE + (3,)),  # normalize pixel values
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.2),
    layers.Dense(num_classes, activation="softmax"),
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

model.summary()

# ---------------------------
# Step 5: Train the model
# ---------------------------
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
)

# ---------------------------
# Step 6: Save the trained model
# ---------------------------
model.save("model.keras")
print("Saved model.keras")

# ---------------------------
# Step 7: Print final results
# ---------------------------
final_train_acc = history.history["accuracy"][-1]
final_val_acc = history.history["val_accuracy"][-1]
print(f"Final training accuracy: {final_train_acc:.2%}")
print(f"Final validation accuracy: {final_val_acc:.2%}")
