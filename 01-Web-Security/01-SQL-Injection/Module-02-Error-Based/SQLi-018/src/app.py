"""SQLi-018: PostgreSQL CHR() Concatenation Error-based"""
from flask import Flask, request, render_template_string
import psycopg2, os
app = Flask(__name__)
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://app_user:app_password@localhost:5432/analyticsdb')
TPL = '''<!DOCTYPE html><html><head><title>Analytics Dashboard</title><style>body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:20px;color:#fff}.container{max-width:800px;margin:auto;background:rgba(255,255,255,0.1);padding:30px;border-radius:15px;backdrop-filter:blur(10px)}.metric{background:rgba(255,255,255,0.2);padding:20px;border-radius:10px;margin:15px 0;display:flex;justify-content:space-between}.metric .value{font-size:2em;font-weight:bold}.error{background:rgba(255,0,0,0.3);padding:15px;border-radius:5px;font-family:monospace}.hint{background:rgba(255,255,0,0.2);padding:15px;border-radius:5px;margin:20px 0}a{color:#fff}</style></head><body><div class="container"><h1>📊 Analytics Dashboard</h1><div class="hint">💡 Lab: PostgreSQL CHR() concatenation error-based</div><p>Metrics: <a href="?id=1">PageViews</a> | <a href="?id=2">Visitors</a> | <a href="?id=3">Conversions</a></p>{% if error %}<div class="error">{{error}}</div>{% endif %}{% if metric %}<div class="metric"><span>{{metric[1]}}</span><span class="value">{{metric[2]}}</span></div>{% endif %}</div></body></html>'''
@app.route('/')
@app.route('/analytics')
def analytics():
    mid = request.args.get('id', '1'); metric, error = None, None
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute(f"SELECT * FROM metrics WHERE id = {mid}")
        metric = cur.fetchone(); cur.close(); conn.close()
    except psycopg2.Error as e: error = str(e)
    return render_template_string(TPL, metric=metric, error=error)
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
