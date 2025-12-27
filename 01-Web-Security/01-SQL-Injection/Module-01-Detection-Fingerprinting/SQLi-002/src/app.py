"""
SQLi-002: Logic-based SQL Injection Detection
Vulnerable News Portal Application (PostgreSQL)

WARNING: This application is intentionally vulnerable for educational purposes.
DO NOT use this code in production!
"""

from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://app_user:app_password@localhost:5432/newsportal')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NewsPortal - Latest News</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Georgia', serif; 
            background: #f5f5f5;
            min-height: 100vh;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px 20px;
            text-align: center;
            color: #fff;
        }
        .header h1 { font-size: 2.8em; margin-bottom: 10px; }
        .header p { color: #aaa; }
        .nav {
            background: #0f3460;
            padding: 15px;
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        .nav a {
            color: #fff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav a:hover, .nav a.active { background: rgba(255,255,255,0.2); }
        .container { max-width: 1000px; margin: 0 auto; padding: 30px 20px; }
        .category-title {
            font-size: 1.5em;
            color: #0f3460;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #e94560;
        }
        .article-count {
            background: #e94560;
            color: #fff;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 15px;
        }
        .articles-list { display: flex; flex-direction: column; gap: 20px; }
        .article-card {
            background: #fff;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .article-card:hover { transform: translateY(-3px); }
        .article-card h3 { 
            color: #0f3460; 
            margin-bottom: 10px;
            font-size: 1.4em;
        }
        .article-card .meta {
            color: #888;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .article-card .content { color: #555; line-height: 1.6; }
        .article-card .footer {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        .article-card .category-tag {
            background: #0f3460;
            color: #fff;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }
        .article-card .views { color: #888; }
        .no-results {
            text-align: center;
            padding: 50px;
            color: #888;
        }
        .hint-box {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px 20px;
            margin: 20px 0;
            color: #856404;
        }
        .categories-sidebar {
            background: #fff;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .categories-sidebar h4 { margin-bottom: 15px; color: #0f3460; }
        .categories-sidebar ul { list-style: none; }
        .categories-sidebar li {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .categories-sidebar a { color: #333; text-decoration: none; }
        .categories-sidebar a:hover { color: #e94560; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 NewsPortal</h1>
        <p>Your trusted source for latest news</p>
    </div>
    
    <nav class="nav">
        <a href="/articles?category=technology">Technology</a>
        <a href="/articles?category=finance">Finance</a>
        <a href="/articles?category=politics">Politics</a>
        <a href="/articles?category=science">Science</a>
        <a href="/articles?category=sports">Sports</a>
        <a href="/articles?category=business">Business</a>
    </nav>
    
    <div class="container">
        <div class="hint-box">
            💡 <strong>Lab Hint:</strong> This category filter might be vulnerable to SQL Injection. 
            Try testing with logic-based payloads like <code>' OR '1'='1</code> or <code>' AND '1'='2</code>
        </div>
        
        {% if category %}
        <h2 class="category-title">
            {{ category|capitalize }} Articles
            <span class="article-count">{{ articles|length }} articles</span>
        </h2>
        {% endif %}
        
        {% if articles %}
        <div class="articles-list">
            {% for article in articles %}
            <div class="article-card">
                <h3>{{ article[1] }}</h3>
                <div class="meta">
                    By {{ article[4] }} • {{ article[5].strftime('%B %d, %Y') if article[5] else 'Unknown date' }}
                </div>
                <div class="content">{{ article[2][:200] }}...</div>
                <div class="footer">
                    <span class="category-tag">{{ article[3] }}</span>
                    <span class="views">👁️ {{ article[6] }} views</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-results">
            <h3>No articles found</h3>
            <p>Try selecting a different category</p>
        </div>
        {% endif %}
        
        <div class="categories-sidebar">
            <h4>All Categories</h4>
            <ul>
                <li><a href="/articles?category=technology">📱 Technology</a></li>
                <li><a href="/articles?category=finance">💰 Finance</a></li>
                <li><a href="/articles?category=politics">🏛️ Politics</a></li>
                <li><a href="/articles?category=science">🔬 Science</a></li>
                <li><a href="/articles?category=sports">⚽ Sports</a></li>
                <li><a href="/articles?category=business">💼 Business</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, articles=None, category=None)

@app.route('/articles')
def articles():
    category = request.args.get('category', '')
    articles = []
    
    if category:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # VULNERABLE: Direct string concatenation - SQL Injection possible!
            sql = f"SELECT * FROM articles WHERE category = '{category}'"
            
            cursor.execute(sql)
            articles = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as err:
            # Not exposing detailed errors in this lab (logic-based detection)
            articles = []
    
    return render_template_string(HOME_TEMPLATE, articles=articles, category=category)

@app.route('/health')
def health():
    return {'status': 'ok', 'database': 'PostgreSQL'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
