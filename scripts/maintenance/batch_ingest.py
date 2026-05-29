#!/usr/bin/env python3
"""
Batch Ingestion and Queue Pop Engine
Reads the generated HTML content from subfiles/batch_payload.json, matches slugs against
subfiles/graduation_queue_stack.json to retrieve physical identities, graduates them using
commit_node.py, marks them as completed in the backlog, and pops them off the GQS stack.
"""

import os
import sys
import json
import subprocess
import shutil

PAYLOAD_PATH = "subfiles/batch_payload.json"
GQS_PATH = "subfiles/graduation_queue_stack.json"
BACKLOG_PATH = "subfiles/expansion_backlog.json"
LOGS_DIR = "logs/graduations"

def print_banner(text):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80)

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
            print(f"  [Backlog] Synchronized '{slug}' status to completed.")
    except Exception as e:
        print(f"  [Backlog Warning] Failed to update backlog for {slug}: {e}")

def main():
    payload_file = PAYLOAD_PATH
    if len(sys.argv) > 1:
        payload_file = sys.argv[1]

    if not os.path.exists(payload_file):
        print(f"Error: Ingestion payload not found at {payload_file}")
        sys.exit(1)

    if not os.path.exists(GQS_PATH):
        print(f"Error: GQS stack file not found at {GQS_PATH}. Run generate_sprint_queue.py first.")
        sys.exit(1)

    # 1. Load files
    with open(payload_file, "r") as f:
        payload = json.load(f)

    with open(GQS_PATH, "r") as f:
        gqs_stack = json.load(f)

    # Convert GQS stack to a quick lookup map by slug
    gqs_map = {item["slug"]: item for item in gqs_stack}

    if not payload:
        print("Notice: Payload file is empty. Nothing to ingest.")
        sys.exit(0)

    print_banner(f"STARTING GQS BATCH INGESTION: {len(payload)} subtopics")

    results = []

    for slug, data in payload.items():
        print(f"\n▶ Ingesting and graduating: \033[1m{slug}\033[0m")
        
        # Retrieve HTML content
        html_content = data.get("content")
        if not html_content:
            print(f"  \033[91m↳ Error: No HTML content found in payload for {slug}\033[0m")
            results.append({"slug": slug, "success": False, "error": "No content in payload"})
            continue

        # Look up metadata in the GQS stack
        stack_entry = gqs_map.get(slug)
        if not stack_entry:
            print(f"  \033[91m↳ Warning: {slug} not found in GQS stack. Proceeding with ad-hoc defaults.\033[0m")
            # If not in GQS, mock an identity or check default files
            identity_data = []
        else:
            identity_data = [stack_entry["identity"]]

        # 2. Write temporary draft and identities files to disk to invoke compile logic cleanly
        temp_draft = f"draft_{slug}.html"
        temp_identities = f"identities_{slug}.json"

        with open(temp_draft, "w") as f:
            f.write(html_content)

        with open(temp_identities, "w") as f:
            json.dump(identity_data, f, indent=4)

        # 3. Compile the node via commit_node.py in a subprocess to reuse stable compilation pipeline
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_path = os.path.join(LOGS_DIR, f"{slug}.log")

        cmd = [
            ".venv/bin/python3", "scripts/maintenance/commit_node.py",
            slug, temp_draft, temp_identities
        ]

        print(f"  [Compiler] Invoking compiler for {slug}...")
        try:
            with open(log_path, 'w') as log_file:
                process = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                )
                log_file.write(process.stdout)
                log_file.write(process.stderr)
            
            print(f"  \033[92m↳ Success: Graduated {slug}! (Logs: {log_path})\033[0m")
            results.append({"slug": slug, "success": True, "error": None})
            
            # Sync backlog status
            update_backlog(slug)

        except subprocess.CalledProcessError as err:
            error_log = err.stdout + "\n" + err.stderr
            with open(log_path, 'w') as log_file:
                log_file.write(error_log)
            print(f"  \033[91m↳ Failure: Compilation failed. See {log_path} for errors.\033[0m")
            results.append({"slug": slug, "success": False, "error": f"Compilation failed. Logs: {log_path}"})

        finally:
            # Clean up temporary draft and identities files
            if os.path.exists(temp_draft):
                os.remove(temp_draft)
            if os.path.exists(temp_identities):
                os.remove(temp_identities)

    # 4. Pop successful graduates off the central GQS stack file
    successful_slugs = {r["slug"] for r in results if r["success"]}
    updated_gqs_stack = [item for item in gqs_stack if item["slug"] not in successful_slugs]

    with open(GQS_PATH, "w") as f:
        json.dump(updated_gqs_stack, f, indent=4)
    print(f"\n[GQS Stack] Popped {len(successful_slugs)} successful nodes off the stack.")
    print(f"            Stack size reduced from {len(gqs_stack)} to {len(updated_gqs_stack)}.")

    # 5. Summarize
    print_banner("BATCH INGESTION REPORT")
    print(f"{'Slug':<30} | {'Status':<12} | {'Error'}")
    print("-"*80)
    for r in results:
        status_str = "\033[92mSUCCESS\033[0m" if r['success'] else "\033[91mFAILED\033[0m"
        err_msg = r['error'] if r['error'] else "n/a"
        print(f"{r['slug']:<30} | {status_str:<21} | {err_msg}")
    print("="*80 + "\n")

    # 6. Self-heal and regenerate central stack if it was partially consumed
    if len(successful_slugs) > 0:
        print("Synchronizing expansion registries...")
        os.system(".venv/bin/python3 scripts/maintenance/sync_backlog.py")
        
        # Refill the GQS stack to maintain full size
        print("Refilling GQS stack with next priority backlog items...")
        stack_limit = len(gqs_stack) # maintain original stack depth
        os.system(f".venv/bin/python3 scripts/maintenance/generate_sprint_queue.py {stack_limit}")

if __name__ == "__main__":
    main()
