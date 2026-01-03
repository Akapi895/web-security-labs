"""SQLi-030: MSSQL Time-based - WAITFOR DELAY"""
from flask import Flask, request, jsonify
import pyodbc
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MSSQL_HOST', 'localhost'),
    'user': os.environ.get('MSSQL_USER', 'sa'),
    'password': os.environ.get('MSSQL_PASSWORD', 'YourStrong@Passw0rd'),
    'database': os.environ.get('MSSQL_DATABASE', 'emaildb')
}

def get_connection():
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_CONFIG['host']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['user']};PWD={DB_CONFIG['password']};TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)

@app.route('/')
def index():
    return '<h1>Email Validator</h1><p>Lab: MSSQL Time-based (WAITFOR DELAY)</p><a href="/validate?email=test@test.com">Test</a>'

@app.route('/validate')
def validate():
    email = request.args.get('email', '')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: Time-based blind
        sql = f"SELECT is_verified FROM email_subscribers WHERE email = '{email}'"
        cursor.execute(sql)
        cursor.fetchone()
        cursor.close()
        conn.close()
    except:
        pass
    
    # Always same response
    return jsonify({"status": "processed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
