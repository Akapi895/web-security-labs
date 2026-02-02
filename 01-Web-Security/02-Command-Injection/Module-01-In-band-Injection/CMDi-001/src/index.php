<?php
/**
 * CMDi-001: Basic Semicolon Separator Injection
 * Vulnerable Network Diagnostic Tool
 * 
 * WARNING: This application is intentionally vulnerable for educational purposes.
 * DO NOT use this code in production!
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Diagnostic Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 { color: #00ff88; font-size: 2.2em; }
        .header p { color: #888; margin-top: 5px; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        .tool-box {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .tool-box h2 { margin-bottom: 20px; color: #00ff88; }
        .ping-form { display: flex; gap: 10px; flex-wrap: wrap; }
        .ping-input {
            flex: 1;
            min-width: 200px;
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .ping-input::placeholder { color: #888; }
        .ping-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            border: none;
            border-radius: 8px;
            color: #000;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .ping-btn:hover { transform: scale(1.05); }
        .output-box {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid rgba(0,255,136,0.3);
        }
        .output-label {
            color: #00ff88;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .hint-box {
            background: rgba(255,193,7,0.1);
            border: 1px solid rgba(255,193,7,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            color: #ffc107;
        }
        .info-box {
            background: rgba(0,150,255,0.1);
            border: 1px solid rgba(0,150,255,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            color: #00d4ff;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 Network Diagnostic Tool</h1>
        <p>Internal IT Infrastructure Testing</p>
    </div>
    <div class="container">
        <div class="tool-box">
            <h2>📡 Ping Utility</h2>
            <p style="color: #aaa; margin-bottom: 20px;">
                Enter an IP address or hostname to check network connectivity.
            </p>
            <form class="ping-form" method="POST" action="">
                <input type="text" name="ip" class="ping-input" 
                       placeholder="Enter IP address (e.g., 127.0.0.1, 8.8.8.8)"
                       value="<?php echo isset($_POST['ip']) ? htmlspecialchars($_POST['ip']) : ''; ?>">
                <button type="submit" class="ping-btn">🚀 Ping</button>
            </form>
            
            <div class="hint-box">
                💡 <strong>Lab Hint:</strong> This diagnostic tool executes system commands. 
                What happens if you can control more than just the IP address?
            </div>
            
            <?php if (isset($_POST['ip']) && !empty($_POST['ip'])): ?>
            <div class="output-box">
                <div class="output-label">📋 Command Output:</div>
<?php
$ip = $_POST['ip'];

// VULNERABLE: Direct string concatenation - Command Injection possible!
$output = shell_exec("ping -c 4 " . $ip);

echo htmlspecialchars($output);
?>
            </div>
            <?php endif; ?>
            
            <div class="info-box">
                ℹ️ <strong>System Info:</strong> Running on Linux server. 
                This tool is for authorized IT personnel only.
            </div>
        </div>
    </div>
</body>
</html>
