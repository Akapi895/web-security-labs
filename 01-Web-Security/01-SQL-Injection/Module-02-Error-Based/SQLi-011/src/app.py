"""SQLi-011: MySQL Double Query Error-based SQLi"""
from flask import Flask, request, render_template_string
import mysql.connector, os
app = Flask(__name__)
DB = {'host': os.environ.get('MYSQL_HOST', 'localhost'), 'user': os.environ.get('MYSQL_USER', 'app_user'), 'password': os.environ.get('MYSQL_PASSWORD', 'app_password'), 'database': os.environ.get('MYSQL_DATABASE', 'blogdb')}
TPL = '''<!DOCTYPE html><html><head><title>TechBlog</title><style>body{font-family:Georgia;background:#f5f5f5;padding:20px}.container{max-width:800px;margin:auto;background:#fff;padding:30px;border-radius:10px}.article{border-left:4px solid #007bff;padding-left:20px;margin:20px 0}.error{background:#fee;padding:15px;border-radius:5px;color:#c00;font-family:monospace;white-space:pre-wrap}.hint{background:#fff3cd;padding:15px;border-radius:5px}a{color:#007bff}</style></head><body><div class="container"><h1>📝 TechBlog</h1><div class="hint">💡 Lab: Double Query (FLOOR+RAND) technique</div><p>Articles: <a href="?id=1">1</a> | <a href="?id=2">2</a> | <a href="?id=3">3</a></p>{% if error %}<div class="error">{{ error }}</div>{% endif %}{% if article %}<div class="article"><h2>{{ article[1] }}</h2><p>{{ article[2] }}</p><small>By {{ article[3] }}</small></div>{% endif %}</div></body></html>'''

@app.route('/')
@app.route('/article')
def article():
    aid = request.args.get('id', '1')
    article, error = None, None
    conn = None
    cur = None
    
    try:
        conn = mysql.connector.connect(**DB)
        cur = conn.cursor()
        query = f"SELECT * FROM articles WHERE id = {aid}"
        
        try:
            cur.execute(query)
            # Try to fetch the first result
            article = cur.fetchone()
            
            # Consume all remaining results to avoid "Unread result found" error
            # This is important for UNION queries
            try:
                cur.fetchall()  # Fetch any remaining rows in current resultset
            except:
                pass
                
        except mysql.connector.Error as exec_err:
            # Duplicate key error from FLOOR+RAND GROUP BY appears here!
            error = str(exec_err)
            
    except Exception as e:
        error = str(e) if not error else error
        
    finally:
        # Proper cleanup
        if cur:
            try:
                cur.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
                
    return render_template_string(TPL, article=article, error=error)

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
