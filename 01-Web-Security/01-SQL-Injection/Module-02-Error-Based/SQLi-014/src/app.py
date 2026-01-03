"""SQLi-014: Oracle UTL_INADDR Error-based"""
from flask import Flask, request, render_template_string
import oracledb, os, time
app = Flask(__name__)
HOST, PORT, SVC, USER, PWD = os.environ.get('ORACLE_HOST','localhost'), os.environ.get('ORACLE_PORT','1521'), os.environ.get('ORACLE_SERVICE','XEPDB1'), os.environ.get('ORACLE_USER','app_user'), os.environ.get('ORACLE_PASSWORD','app_password')

def get_conn(): 
    return oracledb.connect(user=USER, password=PWD, dsn=f"{HOST}:{PORT}/{SVC}")

def init_db():
    """Initialize database tables if not exist"""
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = get_conn()
            cur = conn.cursor()
            
            # Check if tables exist
            cur.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = 'CUSTOMERS'")
            if cur.fetchone()[0] == 0:
                print("[*] Creating tables...")
                
                # Create customers table
                cur.execute("""
                    CREATE TABLE customers (
                        id NUMBER PRIMARY KEY, 
                        name VARCHAR2(100), 
                        email VARCHAR2(100), 
                        tier VARCHAR2(20)
                    )
                """)
                
                # Create secrets table
                cur.execute("""
                    CREATE TABLE secrets (
                        id NUMBER PRIMARY KEY, 
                        name VARCHAR2(100), 
                        value VARCHAR2(255)
                    )
                """)
                
                # Insert data
                cur.execute("INSERT INTO customers VALUES (1, 'Alice Corp', 'alice@example.com', 'Gold')")
                cur.execute("INSERT INTO customers VALUES (2, 'Bob Inc', 'bob@example.com', 'Silver')")
                cur.execute("INSERT INTO secrets VALUES (1, 'sqli_014', 'FLAG{0r4cl3_utl_1n4ddr_3rr0r}')")
                
                conn.commit()
                print("[+] Tables created successfully!")
            else:
                print("[+] Tables already exist")
            
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[!] Database connection attempt {i+1}/{max_retries} failed: {e}")
            time.sleep(2)
    
    print("[!] Failed to initialize database after all retries")
    return False

TPL = '''<!DOCTYPE html><html><head><title>Customer Portal</title><style>body{font-family:Arial;background:#c74634;padding:20px}.container{max-width:700px;margin:auto;background:#fff;padding:30px;border-radius:10px}.error{background:#fee;padding:15px;border-radius:5px;color:#c00;font-family:monospace;white-space:pre-wrap}.hint{background:#fff3cd;padding:15px;border-radius:5px;margin:20px 0}a{color:#c74634}</style></head><body><div class="container"><h1>🏛️ Oracle Customer Portal</h1><div class="hint">💡 Lab: UTL_INADDR error-based SQLi</div><p>Customers: <a href="?id=1">1</a> | <a href="?id=2">2</a></p>{% if error %}<div class="error">{{error}}</div>{% endif %}{% if cust %}<h2>{{cust[1]}}</h2><p>{{cust[2]}} | Tier: {{cust[3]}}</p>{% endif %}</div></body></html>'''

@app.route('/')
@app.route('/customer')
def customer():
    cid = request.args.get('id', '1'); cust, error = None, None
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(f"SELECT * FROM customers WHERE id = {cid}")
        cust = cur.fetchone(); cur.close(); conn.close()
    except oracledb.Error as e: error = str(e)
    return render_template_string(TPL, cust=cust, error=error)

if __name__ == '__main__': 
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
