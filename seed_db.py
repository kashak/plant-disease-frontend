import sqlite3

conn = sqlite3.connect('crop_diseases.db')
cursor = conn.cursor()

sample_data = [
    ('Tomato', 'Early Blight', 'A common fungal disease affecting tomato leaves, stems, and fruit.', 'Dark concentric spots on older leaves.', 'Apply fungicide. Remove infected leaves.', 'Rotate crops. Avoid overhead watering.'),
    ('Tomato', 'Late Blight', 'A fast-spreading destructive disease.', 'Water-soaked spots turning brown/black.', 'Remove infected plants. Apply fungicide.', 'Avoid wetting foliage. Ensure airflow.'),
    ('Tomato', 'Leaf Mold', 'A fungal disease common in humid conditions.', 'Pale yellow spots, olive-green mold underneath.', 'Improve ventilation. Apply fungicide.', 'Reduce humidity. Avoid overhead watering.'),
    ('Tomato', 'healthy', 'No disease detected.', 'Green, undamaged leaves.', 'No treatment necessary.', 'Continue regular care.')
]

cursor.executemany('''
INSERT INTO diseases (crop, disease, description, symptoms, treatment, prevention)
VALUES (?, ?, ?, ?, ?, ?)
''', sample_data)

conn.commit()
conn.close()
print(f"Inserted {len(sample_data)} records")
