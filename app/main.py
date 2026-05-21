from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'db'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        database=os.getenv('DB_NAME', 'tasks')
    )

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/task', methods=['POST'])
def add_task():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "name is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (name) VALUES (%s)", (name,))
    conn.commit()
    task_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    return jsonify({"id": task_id, "name": name}), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tasks), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
