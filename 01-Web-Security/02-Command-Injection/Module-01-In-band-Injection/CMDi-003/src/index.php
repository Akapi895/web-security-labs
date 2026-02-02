<?php
/**
 * CMDi-003: Command Substitution Injection
 * Vulnerable DNS Lookup Service
 * 
 * This lab demonstrates that filtering separators is not enough.
 * Command substitution ($() and ``) can still be exploited.
 * 
 * WARNING: Intentionally vulnerable for educational purposes.
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNS Lookup Service</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #2d1b4e 0%, #1a0a2e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 { color: #a855f7; font-size: 2.2em; }
        .header p { color: #888; margin-top: 5px; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        .lookup-box {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .lookup-box h2 { margin-bottom: 20px; color: #a855f7; }
        .lookup-form { display: flex; gap: 10px; flex-wrap: wrap; }
        .host-input {
            flex: 1;
            min-width: 200px;
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .host-input::placeholder { color: #888; }
        .lookup-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #a855f7, #9333ea);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .lookup-btn:hover { transform: scale(1.05); }
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
            border: 1px solid rgba(168,85,247,0.3);
        }
        .output-label {
            color: #a855f7;
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
        .security-notice {
            background: rgba(76,175,80,0.1);
            border: 1px solid rgba(76,175,80,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            color: #81c784;
            font-size: 0.9em;
        }
        .blocked-list {
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            color: #f87171;
            font-size: 0.9em;
        }
        code {
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 DNS Lookup Service</h1>
        <p>Internal Hosting Infrastructure Tool</p>
    </div>
    <div class="container">
        <div class="lookup-box">
            <h2>🔍 DNS Query Tool</h2>
            <p style="color: #aaa; margin-bottom: 20px;">
                Enter a hostname to perform DNS lookup.
            </p>
            
            <form class="lookup-form" method="POST" action="">
                <input type="text" name="host" class="host-input" 
                       placeholder="Enter hostname (e.g., google.com, github.com)"
                       value="<?php echo isset($_POST['host']) ? htmlspecialchars($_POST['host']) : ''; ?>">
                <button type="submit" class="lookup-btn">🔎 Lookup</button>
            </form>
            
            <div class="security-notice">
                🔒 <strong>Security Enhanced:</strong> This system has been hardened against 
                command injection. Common separators are blocked.
            </div>
            
            <div class="blocked-list">
                🚫 <strong>Blocked Characters:</strong> 
                <code>;</code> <code>|</code> <code>&amp;</code> <code>\n</code> <code>\r</code>
            </div>
            
            <div class="hint-box">
                💡 <strong>Lab Hint:</strong> The developer blocked common command separators.
                But are there other ways to execute commands in shell without separators?
                Think about how shell handles <code>$()</code> and backticks.
            </div>
            
            <?php if (isset($_POST['host']) && !empty($_POST['host'])): ?>
            <?php
            $hostname = $_POST['host'];
            
            // "Enhanced" security filter - blocks common separators
            // BUT MISSES command substitution!
            $dangerous = [';', '|', '&', "\n", "\r", '%0a', '%0d'];
            foreach ($dangerous as $char) {
                $hostname = str_replace($char, '', $hostname);
            }
            
            // Still vulnerable to $() and `` command substitution!
            $output = shell_exec("nslookup " . $hostname . " 2>&1");
            ?>
            
            <div class="output-box">
                <div class="output-label">📋 DNS Lookup Result:</div>
<?php echo htmlspecialchars($output); ?>
            </div>
            <?php endif; ?>
        </div>
    </div>
</body>
</html>
