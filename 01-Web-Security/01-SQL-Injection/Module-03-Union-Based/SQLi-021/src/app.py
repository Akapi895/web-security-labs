"""SQLi-021: MySQL Union-based - Multi Row (GROUP_CONCAT)"""
from flask import Flask, request, render_template_string
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'rootpass'),
    'database': os.environ.get('MYSQL_DATABASE', 'blogdb'),
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📝 Tech Blog</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #f8cdda, #1d2b64);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { text-align: center; color: #aaa; margin-bottom: 30px; }
        .hint {
            background: linear-gradient(90deg, rgba(248,205,218,0.2), rgba(29,43,100,0.2));
            border-left: 4px solid #f8cdda;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        .posts-nav {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .posts-nav h3 { margin-bottom: 15px; }
        .post-links { display: flex; gap: 10px; flex-wrap: wrap; }
        .post-links a {
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 8px;
            color: #f8cdda;
            text-decoration: none;
            transition: background 0.2s;
        }
        .post-links a:hover { background: rgba(255,255,255,0.2); }
        .post-content {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .post-content h2 { color: #f8cdda; margin-bottom: 10px; }
        .post-content .author { color: #888; font-size: 0.9em; margin-bottom: 15px; }
        .post-content .body { line-height: 1.6; }
        .comments {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
        }
        .comments h3 { color: #f8cdda; margin-bottom: 15px; }
        .comment {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .comment .user { color: #f8cdda; font-weight: bold; margin-bottom: 5px; }
        .comment .text { color: #ddd; }
        .error {
            background: rgba(220,53,69,0.2);
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .no-results { color: #888; text-align: center; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Tech Blog</h1>
        <p class="subtitle">Insights and tutorials for developers</p>
        
        <div class="hint">
            💡 <strong>Lab:</strong> MySQL Union-based SQLi - Multi Row (GROUP_CONCAT)
        </div>
        
        <div class="posts-nav">
            <h3>📚 Recent Posts</h3>
            <div class="post-links">
                <a href="/post?id=1">Welcome</a>
                <a href="/post?id=2">Security Tips</a>
                <a href="/post?id=3">MySQL Tips</a>
                <a href="/post?id=4">Docker Guide</a>
            </div>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% elif id %}
        {% if post %}
        <div class="post-content">
            <h2>{{ post.title }}</h2>
            <p class="author">By {{ post.author }}</p>
            <div class="body">{{ post.content }}</div>
        </div>
        {% endif %}
        
        <div class="comments">
            <h3>💬 Comments ({{ comments|length }})</h3>
            {% for comment in comments %}
            <div class="comment">
                <div class="user">{{ comment.username }}</div>
                <div class="text">{{ comment.text }}</div>
            </div>
            {% endfor %}
            {% if not comments %}
            <div class="no-results">No comments yet</div>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE, id=None, post=None, comments=[], error=None)

@app.route('/post')
def post():
    post_id = request.args.get('id', '')
    post_data = None
    comments = []
    error = None
    
    if post_id:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # VULNERABLE: Get comments - returns multiple rows
            sql = f"SELECT username, comment_text FROM comments WHERE post_id = {post_id}"
            cursor.execute(sql)
            rows = cursor.fetchall()
            comments = [{'username': r[0], 'text': r[1]} for r in rows]
            
            # Get post (safe query - using int)
            try:
                safe_id = int(post_id.split()[0])  # Lấy số đầu tiên
                cursor.execute(f"SELECT id, title, content, author FROM posts WHERE id = {safe_id}")
                row = cursor.fetchone()
                if row:
                    post_data = {'id': row[0], 'title': row[1], 'content': row[2], 'author': row[3]}
            except:
                pass
            
            cursor.close()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(TEMPLATE, id=post_id, post=post_data, comments=comments, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
