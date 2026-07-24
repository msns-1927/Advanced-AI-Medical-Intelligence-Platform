import sqlite3

DATABASE_NAME = "medical_history.db"


def create_database():

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT,

            prediction TEXT,

            confidence REAL,

            gradcam_path TEXT,

            medical_report TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()

    print("Database Ready.")


# Insert function
def save_prediction(
        filename,
        prediction,
        confidence,
        gradcam_path,
        medical_report):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO prediction_history (

            filename,

            prediction,

            confidence,

            gradcam_path,

            medical_report

        )

        VALUES (?, ?, ?, ?, ?)

    """, (

        filename,

        prediction,

        confidence,

        gradcam_path,

        medical_report

    ))

    conn.commit()

    conn.close()

    print("Prediction Saved.")


# Read function
def get_history():

    conn = sqlite3.connect(DATABASE_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM prediction_history

        ORDER BY created_at DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]