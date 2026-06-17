from flask import Flask, request
import psycopg2
import os
import time

app = Flask(__name__)

def get_connection():
    for i in range(10):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            print("Connected to PostgreSQL")
            return conn

        except psycopg2.OperationalError:
            print("Waiting for PostgreSQL...")
            time.sleep(5)

    raise Exception("Could not connect to PostgreSQL")

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE
        )
    """)

    conn.commit()

    cur.close()
    conn.close()

init_db()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, title, completed FROM tasks ORDER BY id"
    )

    rows = cur.fetchall()

    tasks = []

    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "completed": row[2]
        })

    cur.close()
    conn.close()

    return tasks

@app.post("/tasks")
def create_task():
    title = request.json["title"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO tasks(title)
        VALUES(%s)
        RETURNING id
        """,
        (title,)
    )

    task_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return {
        "id": task_id,
        "title": title,
        "completed": False
    }, 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
