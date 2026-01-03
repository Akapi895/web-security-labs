"""SQLi-031: PostgreSQL Time-based - pg_sleep"""
from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'database': os.environ.get('POSTGRES_DATABASE', 'apidb')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    return '<h1>Rate Limit API</h1><p>Lab: PostgreSQL Time-based (pg_sleep)</p>'

@app.route('/api/check')
def check():
    key = request.args.get('key', '')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"SELECT rate_limit FROM api_users WHERE api_key = '{key}'"
        cursor.execute(sql)
        cursor.fetchone()
        cursor.close()
        conn.close()
    except:
        pass
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
