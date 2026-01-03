"""SQLi-032: Oracle Time-based - Heavy Query"""
from flask import Flask, request, jsonify
import oracledb
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('ORACLE_HOST', 'localhost'),
    'port': os.environ.get('ORACLE_PORT', '1521'),
    'service': os.environ.get('ORACLE_SERVICE', 'XEPDB1'),
    'user': os.environ.get('ORACLE_USER', 'app_user'),
    'password': os.environ.get('ORACLE_PASSWORD', 'app_password')
}

def get_connection():
    dsn = f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['service']}"
    return oracledb.connect(user=DB_CONFIG['user'], password=DB_CONFIG['password'], dsn=dsn)

@app.route('/')
def index():
    return '<h1>Request Status</h1><p>Lab: Oracle Time-based (Heavy Query)</p>'

@app.route('/status')
def status():
    req_id = request.args.get('id', '')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"SELECT status FROM requests WHERE request_id = '{req_id}'"
        cursor.execute(sql)
        cursor.fetchone()
        cursor.close()
        conn.close()
    except:
        pass
    return jsonify({"status": "processed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
