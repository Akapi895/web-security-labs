"""SQLi-013: MSSQL XML PATH Error-based"""
from flask import Flask, request, jsonify
import pyodbc, os
app = Flask(__name__)
HOST, USER, PWD, DB = os.environ.get('MSSQL_HOST','localhost'), os.environ.get('MSSQL_USER','sa'), os.environ.get('MSSQL_PASSWORD','YourStrong@Passw0rd'), os.environ.get('MSSQL_DATABASE','empdb')
def get_conn(): return pyodbc.connect(f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={HOST};DATABASE={DB};UID={USER};PWD={PWD};TrustServerCertificate=yes')
@app.route('/')
def home(): return '''<h1>Employee API</h1><p>💡 Lab: MSSQL XML PATH</p><a href="/api/employee?id=1">/api/employee?id=1</a>'''
@app.route('/api/employee')
def employee():
    eid = request.args.get('id', '1')
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(f"SELECT * FROM employees WHERE id = {eid}")
        r = cur.fetchone(); cur.close(); conn.close()
        return jsonify({"id": r[0], "name": r[1], "salary": float(r[2])}) if r else jsonify({"error": "Not found"})
    except Exception as e: return jsonify({"error": str(e)}), 500
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
