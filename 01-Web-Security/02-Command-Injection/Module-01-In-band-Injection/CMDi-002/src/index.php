<?php
/**
 * CMDi-002: Pipe Operator Injection
 * Vulnerable Document Preview System
 * 
 * This lab demonstrates that filtering only semicolon is insufficient.
 * Pipe operator and other separators can still be used.
 * 
 * WARNING: Intentionally vulnerable for educational purposes.
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Preview System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 { color: #64b5f6; font-size: 2.2em; }
        .header p { color: #888; margin-top: 5px; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        .preview-box {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .preview-box h2 { margin-bottom: 20px; color: #64b5f6; }
        .file-list {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .file-list h3 { color: #81c784; margin-bottom: 10px; font-size: 0.9em; }
        .file-list ul { list-style: none; padding-left: 10px; }
        .file-list li { 
            color: #aaa; 
            padding: 5px 0;
            font-family: 'Courier New', monospace;
        }
        .file-list li:before { content: "📄 "; }
        .preview-form { display: flex; gap: 10px; flex-wrap: wrap; }
        .file-input {
            flex: 1;
            min-width: 200px;
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .file-input::placeholder { color: #888; }
        .preview-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #64b5f6, #42a5f5);
            border: none;
            border-radius: 8px;
            color: #000;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .preview-btn:hover { transform: scale(1.05); }
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
            border: 1px solid rgba(100,181,246,0.3);
        }
        .output-label {
            color: #64b5f6;
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
        .error-box {
            background: rgba(244,67,54,0.1);
            border: 1px solid rgba(244,67,54,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            color: #ef5350;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📑 Document Preview System</h1>
        <p>Publishing Company Internal Tool</p>
    </div>
    <div class="container">
        <div class="preview-box">
            <h2>📖 Preview Documents</h2>
            <p style="color: #aaa; margin-bottom: 20px;">
                Enter a filename to preview its contents.
            </p>
            
            <div class="file-list">
                <h3>📁 Available Documents:</h3>
                <ul>
                    <li>sample.txt</li>
                    <li>policy.txt</li>
                    <li>notes.txt</li>
                </ul>
            </div>
            
            <form class="preview-form" method="POST" action="">
                <input type="text" name="file" class="file-input" 
                       placeholder="Enter filename (e.g., sample.txt)"
                       value="<?php echo isset($_POST['file']) ? htmlspecialchars($_POST['file']) : ''; ?>">
                <button type="submit" class="preview-btn">👁️ Preview</button>
            </form>
            
            <div class="security-notice">
                🔒 <strong>Security Notice:</strong> This system has been hardened. 
                Command injection via semicolon (;) has been blocked.
            </div>
            
            <div class="hint-box">
                💡 <strong>Lab Hint:</strong> The developer blocked semicolons to prevent command injection.
                Is this protection sufficient? What other shell operators exist?
            </div>
            
            <?php if (isset($_POST['file']) && !empty($_POST['file'])): ?>
            <?php
            $filename = $_POST['file'];
            
            // "Security" filter - INCOMPLETE! Only blocks semicolon
            $filtered = str_replace(';', '', $filename);
            
            // Still vulnerable to pipe and other operators!
            $output = shell_exec("cat /var/www/docs/" . $filtered . " 2>&1");
            ?>
            
            <div class="output-box">
                <div class="output-label">📋 Document Content:</div>
<?php echo htmlspecialchars($output); ?>
            </div>
            <?php endif; ?>
        </div>
    </div>
</body>
</html>
