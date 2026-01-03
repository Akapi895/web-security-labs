"""SQLi-012: MSSQL CONVERT/CAST Error-based"""
from flask import Flask, request, render_template_string
import pyodbc, os
app = Flask(__name__)
HOST, USER, PWD, DB = os.environ.get('MSSQL_HOST','localhost'), os.environ.get('MSSQL_USER','sa'), os.environ.get('MSSQL_PASSWORD','YourStrong@Passw0rd'), os.environ.get('MSSQL_DATABASE','corpdb')
def get_conn(): return pyodbc.connect(f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={HOST};DATABASE={DB};UID={USER};PWD={PWD};TrustServerCertificate=yes')
TPL = '''<!DOCTYPE html><html><head><title>Corporate Directory</title><style>body{font-family:Arial;background:#f5f5f5;padding:20px}.container{max-width:800px;margin:auto;background:#fff;padding:30px;border-radius:10px}input{padding:10px;width:300px}button{padding:10px 20px;background:#0078d4;color:#fff;border:none;cursor:pointer}.error{background:#fee;padding:15px;border-radius:5px;color:#c00;font-family:monospace;white-space:pre-wrap;margin:20px 0}.results{margin-top:20px}.emp{background:#f9f9f9;padding:15px;margin:10px 0;border-radius:5px}.hint{background:#fff3cd;padding:15px;border-radius:5px;margin:20px 0}</style></head><body><div class="container"><h1>🏢 Corporate Directory</h1><div class="hint">💡 Lab: MSSQL CONVERT/CAST error-based SQLi</div><form><input name="q" placeholder="Search employees..." value="{{q}}"><button>Search</button></form>{% if error %}<div class="error">{{error}}</div>{% endif %}<div class="results">{% for e in emps %}<div class="emp"><strong>{{e[1]}}</strong><br>{{e[2]}} | {{e[3]}}</div>{% endfor %}</div></div></body></html>'''
@app.route('/')
@app.route('/search')
def search():
    q = request.args.get('q', ''); emps, error = [], None
    if q:
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute(f"SELECT * FROM employees WHERE name LIKE '%{q}%'")
            emps = cur.fetchall(); cur.close(); conn.close()
        except Exception as e: error = str(e)
    return render_template_string(TPL, q=q, emps=emps, error=error)
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
