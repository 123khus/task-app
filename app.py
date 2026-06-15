from flask import Flask, request
import json
import os

app = Flask(__name__)

DATA_FILE = "/data/tasks.json"

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE) as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/tasks")
def get_tasks():
    return load_tasks()

@app.post("/tasks")
def create_task():
    tasks = load_tasks()

    task = {
        "id": len(tasks) + 1,
        "title": request.json["title"],
        "completed": False
    }

    tasks.append(task)
    save_tasks(tasks)

    return task, 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
