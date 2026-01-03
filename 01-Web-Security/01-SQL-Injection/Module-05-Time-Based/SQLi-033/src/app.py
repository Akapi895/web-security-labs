"""SQLi-033: MySQL Time-based via Cookie"""
from flask import Flask, request, jsonify
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'rootpass'),
    'database': os.environ.get('MYSQL_DATABASE', 'sessiondb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

@app.route('/')
def index():
    session_id = request.cookies.get('session_id', '')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"SELECT user_id FROM sessions WHERE session_id = '{session_id}'"
        cursor.execute(sql)
        cursor.fetchone()
        cursor.close()
        conn.close()
    except:
        pass
    return '<h1>Session Manager</h1><p>Lab: MySQL Time-based via Cookie</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
