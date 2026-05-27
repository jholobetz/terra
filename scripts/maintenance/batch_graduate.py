import sys
import os
import json
import subprocess
from datetime import datetime

LOGS_DIR = "logs/graduations"
BACKLOG_PATH = "subfiles/expansion_backlog.json"

def print_table(results):
    """Outputs a beautiful, structured summary table of the batch graduation."""
    print("\n" + "="*80)
    print(" BATCH GRADUATION SUMMARY REPORT".center(80))
    print("="*80)
    print(f"{'Slug':<28} | {'Status':<10} | {'Words':<6} | {'Links':<6} | {'Formulas':<8} | {'Shield'}")
    print("-"*80)
    
    for r in results:
        status_str = "\033[92mSUCCESS\033[0m" if r['success'] else "\033[91mFAILED\033[0m"
        shield_str = "\033[92m✓ SECURE\033[0m" if r['shield_secure'] else "\033[91m⚠ ERROR\033[0m"
        print(f"{r['slug']:<28} | {status_str:<19} | {r['words']:<6} | {r['links']:<6} | {r['formulas']:<8} | {shield_str}")
        if r['error_msg']:
            print(f"  \033[90m↳ Error: {r['error_msg']}\033[0m")
            
    print("="*80 + "\n")

def update_backlog(slug):
    """Marks a graduated slug as completed in expansion_backlog.json."""
    if not os.path.exists(BACKLOG_PATH):
        return
        
    try:
        with open(BACKLOG_PATH, 'r') as f:
            backlog = json.load(f)
            
        updated = False
        for entry in backlog:
            if entry.get('suggested_slug') == slug:
                if entry.get('status') != 'completed':
                    entry['status'] = 'completed'
                    updated = True
                    
        if updated:
            with open(BACKLOG_PATH, 'w') as f:
                json.dump(backlog, f, indent=4)
            print(f"  [Backlog] Synchronized '{slug}' to completed.")
    except Exception as e:
        print(f"  [Backlog Warning] Failed to update backlog for {slug}: {e}")

def graduate_slug(slug):
    """Graduates a single slug using its specific draft and identities templates."""
    print(f"\n▶ Starting graduation for: \033[1m{slug}\033[0m")
    
    # 1. Resolve draft and identities file paths
    draft_file = f"draft_{slug}.html"
    identities_file = f"identities_{slug}.json"
    
    # Fallbacks to default names if specific ones do not exist
    if not os.path.exists(draft_file):
        draft_file = "draft.html"
    if not os.path.exists(identities_file):
        identities_file = "identities.json"
        
    if not os.path.exists(draft_file):
        return {
            'slug': slug, 'success': False, 'words': 0, 'links': 0, 'formulas': 0, 
            'shield_secure': False, 'error_msg': f"No draft file found (checked '{f'draft_{slug}.html'}' and 'draft.html')"
        }
        
    # 2. Run compilation as a subprocess
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_path = os.path.join(LOGS_DIR, f"{slug}.log")
    
    cmd = [
        ".venv/bin/python3", "scripts/maintenance/commit_node.py", 
        slug, draft_file
    ]
    if os.path.exists(identities_file):
        cmd.append(identities_file)
        
    print(f"  [Compiler] Compiling using {draft_file} and {identities_file}...")
    
    try:
        with open(log_path, 'w') as log_file:
            process = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            log_file.write(process.stdout)
            log_file.write(process.stderr)
            
        output = process.stdout
    except subprocess.CalledProcessError as err:
        error_log = err.stdout + "\n" + err.stderr
        with open(log_path, 'w') as log_file:
            log_file.write(error_log)
        return {
            'slug': slug, 'success': False, 'words': 0, 'links': 0, 'formulas': 0, 
            'shield_secure': False, 'error_msg': f"Compilation failed. See {log_path} for logs."
        }
        
    # 3. Parse stats from stdout to populate report
    words = 0
    links = 0
    formulas = 0
    shield_secure = "✓ SHIELD SECURE" in output
    
    # Parse stats from Integrity Shield block: e.g. "Stats:  6 links, 1 formula refs."
    for line in output.split("\n"):
        if "Stats:" in line:
            import re
            links_match = re.search(r"(\d+)\s+links", line)
            f_match = re.search(r"(\d+)\s+formula\s+refs", line)
            if links_match:
                links = int(links_match.group(1))
            if f_match:
                formulas = int(f_match.group(1))
        if "word count too low" in line:
            # Extract word count if low depth warning occurred
            import re
            wc_match = re.search(r"word count too low\s+\((\d+)\)", line)
            if wc_match:
                words = int(wc_match.group(1))
                
    # If no low depth warning occurred, calculate word count directly from HTML draft
    if words == 0:
        try:
            with open(draft_file, 'r') as f:
                content = f.read()
                import re
                text_only = re.sub(r'<[^>]+>', '', content)
                words = len(text_only.split())
        except Exception:
            pass
            
    # 4. Synchronize Backlog Status
    update_backlog(slug)
    
    # 5. Clean up specific draft files to keep workspace pristine
    if draft_file == f"draft_{slug}.html":
        os.remove(draft_file)
    if identities_file == f"identities_{slug}.json":
        os.remove(identities_file)
        
    print(f"  [Status] Successfully graduated {slug}! (Logs saved to {log_path})")
    
    return {
        'slug': slug, 'success': True, 'words': words, 'links': links, 'formulas': formulas,
        'shield_secure': shield_secure, 'error_msg': ""
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_graduate.py <slug1> [slug2] [slug3] ...")
        sys.exit(1)
        
    slugs = sys.argv[1:]
    results = []
    
    print(f"\n============================================================")
    print(f" INITIATING BATCH GRADUATION: {len(slugs)} subtopics")
    print(f"============================================================")
    
    for slug in slugs:
        res = graduate_slug(slug)
        results.append(res)
        
    print_table(results)
    
    # Set exit status
    if any(not r['success'] or not r['shield_secure'] for r in results):
        sys.exit(1)

if __name__ == "__main__":
    main()
