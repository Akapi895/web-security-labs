"""SQLi-034: PostgreSQL Time-based via User-Agent"""
from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DATABASE', 'botdb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '')
    ip = request.remote_addr
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: User-Agent in SQL
        sql = f"INSERT INTO visitors (user_agent, ip_address) VALUES ('{user_agent}', '{ip}')"
        print(f"[DEBUG] SQL: {sql}", flush=True)
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
    
    return '<h1>Bot Detection</h1><p>Lab: PostgreSQL Time-based via User-Agent</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
