"""SQLi-016: Oracle XMLType Error-based"""
from flask import Flask, request, render_template_string
import oracledb, os
app = Flask(__name__)
HOST, PORT, SVC, USER, PWD = os.environ.get('ORACLE_HOST','localhost'), os.environ.get('ORACLE_PORT','1521'), os.environ.get('ORACLE_SERVICE','XEPDB1'), os.environ.get('ORACLE_USER','app_user'), os.environ.get('ORACLE_PASSWORD','app_password')
def get_conn(): return oracledb.connect(user=USER, password=PWD, dsn=f"{HOST}:{PORT}/{SVC}")
TPL = '''<!DOCTYPE html><html><head><title>Data Export</title><style>body{font-family:Arial;background:#2d2d2d;color:#fff;padding:20px}.container{max-width:700px;margin:auto;background:#1a1a1a;padding:30px;border-radius:10px}.error{background:#5c1a1a;padding:15px;border-radius:5px;font-family:monospace}.hint{background:#3d3d00;padding:15px;border-radius:5px;margin:20px 0}a{color:#ffc107}</style></head><body><div class="container"><h1>📤 Data Export</h1><div class="hint">💡 Lab: Oracle XMLType error-based</div><p>Exports: <a href="?id=1">1</a> | <a href="?id=2">2</a></p>{% if error %}<div class="error">{{error}}</div>{% endif %}{% if exp %}<h2>{{exp[1]}}</h2><pre>{{exp[2]}}</pre>{% endif %}</div></body></html>'''
@app.route('/')
@app.route('/export')
def export():
    eid = request.args.get('id', '1'); exp, error = None, None
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(f"SELECT * FROM exports WHERE id = {eid}")
        row = cur.fetchone()
        if row:
            # Convert CLOB to string
            exp = (row[0], row[1], row[2].read() if hasattr(row[2], 'read') else str(row[2]))
        cur.close(); conn.close()
    except oracledb.Error as e: error = str(e)
    return render_template_string(TPL, exp=exp, error=error)
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
