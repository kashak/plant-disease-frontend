from PIL import Image
import numpy as np

def preprocess_image(image_path, target_size=(224, 224)):
    image = Image.open(image_path)
    image = image.convert("RGB")
    image = image.resize(target_size)
    image_array = np.array(image)
    normalized_array = image_array / 255.0
    return normalized_array, image  # also return the resized PIL image


if __name__ == "__main__":
    result, resized_image = preprocess_image("test_leaf.jpg")

    print("Shape:", result.shape)
    print("Min value:", result.min())
    print("Max value:", result.max())

    # Save the resized image so you can visually inspect it
    resized_image.save("preprocessed_preview.jpg")
    print("Saved preprocessed_preview.jpg — open it to check the resize looks correct")