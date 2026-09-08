import sqlite3

conn = sqlite3.connect("crop_diseases.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop TEXT NOT NULL,
    disease TEXT NOT NULL,
    description TEXT,
    symptoms TEXT,
    treatment TEXT,
    prevention TEXT
)
''')

conn.commit()
conn.close()
print("Table diseases created successfully")
