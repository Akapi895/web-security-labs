"""SQLi-045: MySQL UNION Keyword Filter Bypass"""
from flask import Flask, request, render_template_string
import pymysql
import os
import re

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'appuser'),
    'password': os.environ.get('MYSQL_PASSWORD', 'apppass123'),
    'database': os.environ.get('MYSQL_DATABASE', 'blogdb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

# IDS: Block UNION keyword (basic bypass detection)
def ids_check(user_input):
    """IDS that blocks UNION keyword - can be bypassed with MySQL comments"""
    # Strip basic inline comments /**/ but miss versioned comments /*!...*/
    cleaned = re.sub(r'/\*\*/', '', user_input)
    
    if re.search(r'union', cleaned, re.IGNORECASE):
        return False, "Potential SQL injection detected! UNION keyword is blocked."
    return True, None

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📰 SecureBlog - Articles</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #2d3436 0%, #000000 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { text-align: center; color: rgba(255,255,255,0.7); margin-bottom: 30px; }
        .alert {
            background: rgba(220,53,69,0.2);
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .article-box {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .article {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }
        .article h3 { color: #74b9ff; margin-bottom: 10px; }
        .article p { color: rgba(255,255,255,0.8); }
        .article .meta { color: rgba(255,255,255,0.5); font-size: 0.9em; margin-top: 10px; }
        .error {
            background: rgba(220,53,69,0.3);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .nav a {
            color: #74b9ff;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }
        .nav a:hover { background: rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <h1>📰 SecureBlog</h1>
        <p class="subtitle">Security Articles & News</p>
        
        <div class="alert">
            🛡️ <strong>IDS Protected:</strong> SQL injection keywords are monitored and blocked.
        </div>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/article?id=1">Article 1</a>
            <a href="/article?id=2">Article 2</a>
            <a href="/article?id=3">Article 3</a>
        </div>
        
        {% if error %}
        <div class="error">⚠️ {{ error }}</div>
        {% endif %}
        
        <div class="article-box">
            {% if articles %}
                {% for article in articles %}
                <div class="article">
                    <h3>{{ article[1] }}</h3>
                    <p>{{ article[2] }}</p>
                    <div class="meta">By {{ article[3] }} | ID: {{ article[0] }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p>No articles found.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content, author FROM articles")
        articles = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template_string(TEMPLATE, articles=articles, error=None)
    except Exception as e:
        return render_template_string(TEMPLATE, articles=None, error=str(e))

@app.route('/article')
def article():
    article_id = request.args.get('id', '1')
    articles = None
    error = None
    
    # IDS Check - Block UNION keyword
    is_safe, ids_error = ids_check(article_id)
    if not is_safe:
        return render_template_string(TEMPLATE, articles=None, error=ids_error)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # VULNERABLE: SQL Injection (UNION filter can be bypassed)
        sql = f"SELECT id, title, content, author FROM articles WHERE id = {article_id}"
        cursor.execute(sql)
        articles = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        error = f"Database error: {str(e)}"
    
    return render_template_string(TEMPLATE, articles=articles, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
