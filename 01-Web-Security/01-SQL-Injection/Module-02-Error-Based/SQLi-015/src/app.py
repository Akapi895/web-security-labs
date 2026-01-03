"""SQLi-015: Oracle CTXSYS Error-based"""
from flask import Flask, request, render_template_string
import oracledb, os, time

app = Flask(__name__)

# Database configuration
HOST = os.environ.get('ORACLE_HOST', 'localhost')
PORT = os.environ.get('ORACLE_PORT', '1521')
SVC = os.environ.get('ORACLE_SERVICE', 'FREEPDB1')
USER = os.environ.get('ORACLE_USER', 'app_user')
PWD = os.environ.get('ORACLE_PASSWORD', 'app_password')

def get_conn(): 
    return oracledb.connect(user=USER, password=PWD, dsn=f"{HOST}:{PORT}/{SVC}")

def check_ctxsys_available(conn):
    """Check if CTXSYS.DRITHSX is available"""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM user_tab_privs 
            WHERE table_name = 'DRITHSX' 
            AND owner = 'CTXSYS'
            AND privilege = 'EXECUTE'
        """)
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    except:
        return False

def init_db():
    """Initialize database connection and verify setup"""
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = get_conn()
            cur = conn.cursor()
            
            # Check if tables exist
            cur.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = 'REPORTS'")
            if cur.fetchone()[0] == 0:
                print("[!] Tables not found - init.sql may not have run yet")
                print("[→] Waiting for database initialization...")
            else:
                print("[+] Database initialized successfully!")
                
                # Check CTXSYS availability
                print("\n=== CTXSYS Availability ===")
                has_ctxsys = check_ctxsys_available(conn)
                
                if has_ctxsys:
                    print("[✓] CTXSYS.DRITHSX.SN: AVAILABLE")
                    print("    Example: 1 AND 1=CTXSYS.DRITHSX.SN(1,(SELECT user FROM dual))--")
                else:
                    print("[✗] CTXSYS.DRITHSX.SN: NOT AVAILABLE")
                    print("[→] Oracle Text may not be installed")
                
                print("===========================\n")
            
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[!] Connection attempt {i+1}/{max_retries} failed: {e}")
            time.sleep(2)
    
    print("[!] Failed to connect to database after all retries")
    return False

# HTML template
TPL = '''<!DOCTYPE html>
<html>
<head>
    <title>Report Generator</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: #fff; padding: 20px; }
        .container { max-width: 700px; margin: auto; background: #16213e; padding: 30px; border-radius: 10px; }
        .error { background: #5c1a1a; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }
        .hint { background: #3d3d00; padding: 15px; border-radius: 5px; margin: 20px 0; }
        a { color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Report Generator</h1>
        <div class="hint">
            💡 <strong>Lab: Oracle CTXSYS Error-based SQLi</strong><br>
            Technique: CTXSYS.DRITHSX.SN<br>
            Database: Oracle Free (with Oracle Text)
        </div>
        <p>Reports: <a href="?id=1">Q1</a> | <a href="?id=2">Q2</a></p>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        {% if rpt %}
        <h2>{{ rpt[1] }}</h2>
        <p>{{ rpt[2] }}</p>
        {% endif %}
    </div>
</body>
</html>'''

@app.route('/')
@app.route('/report')
def report():
    rid = request.args.get('id', '1')
    rpt, error = None, None
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Vulnerable query - directly concatenating user input
        cur.execute(f"SELECT * FROM reports WHERE id = {rid}")
        row = cur.fetchone()
        
        # Convert CLOB to string if needed
        if row:
            rpt = (row[0], row[1], row[2].read() if hasattr(row[2], 'read') else str(row[2]))
        
        cur.close()
        conn.close()
    except oracledb.Error as e:
        error = str(e)
    
    return render_template_string(TPL, rpt=rpt, error=error)

if __name__ == '__main__': 
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

