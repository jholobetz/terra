import os
import time
import json
import subprocess
import sys

INBOX = "scripts/maintenance/inbox"
LOG_FILE = "scripts/maintenance/watcher.log"
os.makedirs(INBOX, exist_ok=True)

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    print(message)

log("Watcher started. Monitoring " + INBOX)

while True:
    try:
        files = [f for f in os.listdir(INBOX) if f.endswith(".json")]
        for f in files:
            file_path = os.path.join(INBOX, f)
            log(f"Detected trigger: {f}")
            
            with open(file_path, "r") as j:
                try:
                    data = json.load(j)
                    slug = data.get('slug')
                    html_path = data.get('html')
                    ident_path = data.get('identities')
                    
                    if not slug or not html_path:
                        log(f"Invalid trigger data in {f}")
                        os.remove(file_path)
                        continue
                        
                    log(f"Executing commit for: {slug}")
                    
                    # Construct command
                    cmd = ["python3", "scripts/maintenance/commit_node.py", slug, html_path]
                    if ident_path:
                        cmd.append(ident_path)
                    
                    # Run commit script
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True,
                        env=os.environ.copy()
                    )
                    
                    if result.returncode == 0:
                        log(f"SUCCESS: {slug} committed.")
                        log(result.stdout)
                    else:
                        log(f"FAILURE: {slug} failed with code {result.returncode}")
                        log(result.stderr)
                        log(result.stdout)
                        
                except Exception as e:
                    log(f"Error processing {f}: {str(e)}")
            
            os.remove(file_path)
            log(f"Removed trigger: {f}")
            
    except Exception as e:
        log(f"Watcher loop error: {str(e)}")
        
    time.sleep(1)
