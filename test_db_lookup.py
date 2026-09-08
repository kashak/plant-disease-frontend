import sqlite3

def get_disease_info(disease_name: str):
    conn = sqlite3.connect("crop_diseases.db")
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


# Test with a disease name that should exist in your seeded data
result = get_disease_info("Early Blight")
print(result)
result2 = get_disease_info("Some Made Up Disease")
print(result2)
import sqlite3
conn = sqlite3.connect("crop_diseases.db")
cursor = conn.cursor()
cursor.execute("SELECT disease FROM diseases")
print(cursor.fetchall())
conn.close()