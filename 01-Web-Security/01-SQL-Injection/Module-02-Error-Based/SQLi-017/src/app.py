"""SQLi-017: PostgreSQL CAST Error-based"""
from flask import Flask, request, render_template_string
import psycopg2, os
app = Flask(__name__)
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://app_user:app_password@localhost:5432/searchdb')
TPL = '''<!DOCTYPE html><html><head><title>Search</title><style>body{font-family:Arial;background:#2d3436;color:#fff;padding:20px}.container{max-width:700px;margin:auto;background:#636e72;padding:30px;border-radius:10px}input{padding:10px;width:300px}button{padding:10px 20px;background:#00b894;color:#fff;border:none}.error{background:#d63031;padding:15px;border-radius:5px;font-family:monospace;white-space:pre-wrap;margin:20px 0}.hint{background:#fdcb6e;color:#2d3436;padding:15px;border-radius:5px;margin:20px 0}.item{background:#2d3436;padding:15px;margin:10px 0;border-radius:5px}</style></head><body><div class="container"><h1>🔍 Search</h1><div class="hint">💡 Lab: PostgreSQL CAST to numeric error-based</div><form><input name="q" placeholder="Search..." value="{{q}}"><button>Search</button></form>{% if error %}<div class="error">{{error}}</div>{% endif %}{% for i in items %}<div class="item"><strong>{{i[1]}}</strong>: {{i[2]}}</div>{% endfor %}</div></body></html>'''
@app.route('/')
@app.route('/search')
def search():
    q = request.args.get('q', ''); items, error = [], None
    if q:
        try:
            conn = psycopg2.connect(DB_URL); cur = conn.cursor()
            cur.execute(f"SELECT * FROM items WHERE name ILIKE '%{q}%'")
            items = cur.fetchall(); cur.close(); conn.close()
        except psycopg2.Error as e: error = str(e)
    return render_template_string(TPL, q=q, items=items, error=error)
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
