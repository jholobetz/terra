#!/usr/bin/env python3
"""
🪐 Physics Lab - Unified GQS Sprint Orchestrator with Guardrails
Manages autonomous graduation sprints with git savepoints, static syntax checks,
compilation arrests, integrity audits, and self-healing transaction rollbacks.
"""

import os
import sys
import re
import json
import subprocess
from datetime import datetime

# Path constants
PAYLOAD_PATH = "subfiles/batch_payload.json"
SHARDS_DIR = "app/config/content"

def print_banner(text, color_code="96"):
    """Prints a styled terminal banner."""
    print("=" * 80)
    print(f"\033[1;{color_code}m{text.center(80)}\033[0m")
    print("=" * 80)

def run_command(args, shell=False):
    """Runs a subprocess command and returns (exit_code, stdout, stderr)."""
    try:
        res = subprocess.run(
            args,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return -1, "", str(e)

def get_git_savepoint():
    """Gets the current git commit hash to act as a savepoint."""
    code, out, _ = run_command(["git", "rev-parse", "HEAD"])
    if code != 0:
        print("\033[91m⚠️ Error: Workspace is not a git repository or git is unavailable.\033[0m")
        sys.exit(1)
    return out.strip()

def rollback_to_savepoint(savepoint, committed_pre_flight):
    """Executes a hard reset to restore the codebase to the clean savepoint and rolls back the savepoint commit."""
    print(f"\n\033[1;91m💥 CRITICAL QUALITY GATE FAILURE: Initiating automatic transaction rollback...\033[0m")
    code, _, err = run_command(["git", "reset", "--hard", savepoint])
    if code == 0:
        if committed_pre_flight:
            # Rollback the pre-flight commit to leave changes uncommitted
            run_command(["git", "reset", "HEAD~1"])
            print(f"\033[92m✓ ROLLBACK SUCCESSFUL: Restored workspace state to uncommitted changes before GQS sprint.\033[0m")
        else:
            print(f"\033[92m✓ ROLLBACK SUCCESSFUL: Restored workspace state to clean savepoint commit {savepoint[:8]}.\033[0m")
    else:
        print(f"\033[91m⚠️ CRITICAL ERROR: Git rollback failed. Error: {err}\033[0m")
    sys.exit(1)

def run_pre_flight():
    """Ensures we have a clean git tree or commits intermediate files safely."""
    print("🤖 Running pre-flight workspace verification...")
    # Check git status
    code, out, _ = run_command(["git", "status", "--porcelain"])
    committed = False
    if code == 0 and out.strip():
        print("📝 Staging uncommitted changes and creating an automated pre-flight savepoint...")
        run_command(["git", "add", "."])
        run_command(["git", "commit", "-m", f"chore: automated pre-flight GQS savepoint {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        committed = True
    return get_git_savepoint(), committed

def run_syntax_guards(payload_path):
    """Scans subfiles/batch_payload.json to verify that written prose adheres to OPS guidelines."""
    print("🛡️ [Guardrail Stage 1] Running static syntax and OPS style checks...")
    
    if not os.path.exists(payload_path):
        print(f"Error: Ingestion payload not found at {payload_path}")
        return False
        
    with open(payload_path, "r") as f:
        try:
            payload = json.load(f)
        except Exception as e:
            print(f"\033[91mSchema Error: Failed to parse payload JSON. Error: {e}\033[0m")
            return False

    violations = []
    
    for slug, data in payload.items():
        title = data.get("title", "")
        content = data.get("content", "")
        
        # Check if the content is still scaffolded placeholders
        if "[Paragraph 1" in content or "OPS In-Media-Res" in content:
            violations.append(f"[{slug}] Content is still a scaffolded placeholder. Please write the actual prose first.")
            continue
            
        # Check for placeholder identity/equations
        if "placeholder" in content.lower() or "placeholder" in title.lower():
            violations.append(f"[{slug}] Placeholder Violation: Content or title contains scaffolded 'PLACEHOLDER' text in the math block or title. Please replace it with a mathematically localized, topic-specific equation.")

            
        # 1. Parse paragraphs
        paragraphs = re.findall(r"<p>(.*?)</p>", content, re.DOTALL)
        if not paragraphs:
            violations.append(f"[{slug}] No valid HTML paragraphs (<p>...</p>) found.")
            continue
            
        # 2. Continuous prose checks (Lists, headers, markdown residues)
        if "<li>" in content or "<ul>" in content or "<ol>" in content:
            violations.append(f"[{slug}] Continuous prose violation: list elements (<li>, <ul>) are strictly forbidden.")
        if re.search(r"<h[1-6]>", content):
            violations.append(f"[{slug}] Continuous prose violation: heading elements (<h3>, etc.) are strictly forbidden inside subtopic content.")
        if "**" in content or "__" in content:
            violations.append(f"[{slug}] Markdown residue violation: double asterisks (**) or underscores (__) are forbidden. Use <strong> instead.")
            
        # Check for un-delimited display math blocks
        math_displays_raw = re.findall(r'<div class="math-display"[^>]*>(.*?)</div>', content, re.DOTALL)
        for i, display in enumerate(math_displays_raw):
            if not re.search(r'^\\{1,2}\[|^\\{1,2}\(|^\\{1,2}\]|\\{1,2}\]$|\\{1,2}\)$', display.strip()):
                violations.append(f"[{slug}] Math display violation: Equation inside <div class=\"math-display\"> is missing standard delimiters \\\\ [ and \\\\ ]. Delimiters are required for the SVG compiler to recognize and process the LaTeX.")

            
        # 3. Word count check (650 to 1,000 words)
        content_clean = re.sub(r"<[^>]*>", " ", content)  # Strip tags
        content_clean = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", " ", content_clean) # Strip LaTeX blocks for word counting
        words = [w for w in re.findall(r"\w+", content_clean)]
        word_count = len(words)
        
        if word_count < 650 or word_count > 1000:
            violations.append(f"[{slug}] Word count violation: Total words is {word_count} (must be strictly between 650 and 1,000 words).")

        # 4. In Media Res lead check
        first_para = paragraphs[0]
        first_para_clean = re.sub(r"<[^>]*>", " ", first_para) # Strip tags
        first_para_words = [w.lower() for w in re.findall(r"\w+", first_para_clean)[:25]]
        first_25_str = " ".join(first_para_words)
        
        # Forbidden starters
        if first_para_words and (first_para_words[0] in ["this", "the"] and any(starter in first_25_str for starter in ["concept refers", "is the study", "refers to", "is a fundamental", "is defined as"])):
            violations.append(f"[{slug}] In Media Res violation: Starter phrase represents a forbidden definition format.")
            
        # Title check in first 15 words
        title_words = [w.lower() for w in re.findall(r"\w+", title)]
        title_str = " ".join(title_words)
        first_15_str = " ".join(first_para_words[:15])
        
        # Check if a substantial part of the title appears in the first 15 words
        if title_words and any(w in first_15_str for w in title_words if len(w) > 4) and title_str in first_15_str:
            violations.append(f"[{slug}] In Media Res violation: Title '{title}' is mentioned in the first 15 words of the opening paragraph.")

    if violations:
        print(f"\n\033[91m❌ OPS STYLE VIOLATIONS FOUND ({len(violations)}):\033[0m")
        for v in violations:
            print(f"  - {v}")
        return False
        
    print("\033[92m✓ [Guardrail Stage 1 PASS] All drafts conform to OPS qualitative gates.\033[0m")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="🪐 Physics Lab GQS Sprint Orchestrator")
    parser.add_argument("-c", "--count", type=int, default=3, help="Number of queue targets to process")
    parser.add_argument("--dry-run", action="store_true", help="Perform syntax checks without ingesting")
    args = parser.parse_args()

    print_banner("GQS SPRINT ORCHESTRATOR: AUTOMATED QUALITY HARNESS")
    
    # 1. Pre-flight Git checkpoint
    savepoint, committed_savepoint = run_pre_flight()
    print(f"\033[92m✓ Pre-flight savepoint recorded: {savepoint[:8]} (committed: {committed_savepoint})\033[0m\n")

    # If payload is empty, check if we need to template
    if not os.path.exists(PAYLOAD_PATH) or os.path.getsize(PAYLOAD_PATH) == 2:
        print(f"Ingestion payload is empty. Scaffolding next {args.count} targets...")
        code, out, err = run_command([".venv/bin/python3", "gqs.py", "template", str(args.count)])
        if code != 0:
            print(f"\033[91mScaffolding failed: {err or out}\033[0m")
            if committed_savepoint:
                run_command(["git", "reset", "HEAD~1"])
            sys.exit(1)
        print(out)
        print("\033[93mNotice: Scaffolded templates generated. Please write the prose in subfiles/batch_payload.json before running again.\033[0m")
        if committed_savepoint:
            # Revert the savepoint commit so the template remains as uncommitted change
            run_command(["git", "reset", "HEAD~1"])
        sys.exit(0)

    # 2. Guardrail Stage 1: Syntax & OPS checks
    if not run_syntax_guards(PAYLOAD_PATH):
        # We don't rollback yet because the user is editing subfiles/batch_payload.json local draft
        print("\033[93mNotice: Ingestion aborted due to style violations. Workspace preserved for correction.\033[0m")
        if committed_savepoint:
            run_command(["git", "reset", "HEAD~1"])
        sys.exit(1)

    if args.dry_run:
        print("\033[92m✓ Dry-run completed. No compilation was performed.\033[0m")
        if committed_savepoint:
            run_command(["git", "reset", "HEAD~1"])
        sys.exit(0)

    # Read payload slugs to run targeted audits later
    with open(PAYLOAD_PATH, "r") as f:
        payload = json.load(f)
    slugs_to_audit = list(payload.keys())

    # 3. Guardrail Stage 2: Compilation & Ingestion
    print("\n🚀 [Guardrail Stage 2] Initiating compilation and database ingestion...")
    print("Ingesting: " + ", ".join(slugs_to_audit))
    
    code, out, err = run_command([".venv/bin/python3", "gqs.py", "ingest"])
    if code != 0 or "FAILED" in out:
        print(f"\033[91mCompilation Error output:\n{err or out}\033[0m")
        rollback_to_savepoint(savepoint, committed_savepoint)
        
    print("\033[92m✓ [Guardrail Stage 2 PASS] Ingestion and compilation completed successfully.\033[0m")

    # 4. Guardrail Stage 3: Post-Ingestion Integrity Audits
    print("\n🛡️ [Guardrail Stage 3] Initiating targeted integrity shield audits...")
    for slug in slugs_to_audit:
        print(f"Auditing graduated node '{slug}'...")
        code, out, err = run_command([".venv/bin/python3", "integrity_shield.py", slug])
        if code != 0 or "ERRORS FOUND" in out:
            print(f"\033[91mAudit failed for '{slug}' output:\n{out}\033[0m")
            rollback_to_savepoint(savepoint, committed_savepoint)
            
    print("\033[92m✓ [Guardrail Stage 3 PASS] All graduated nodes successfully passed integrity audits.\033[0m")

    # 5. Success Finalization & Metadata commit
    print("\n📝 Finalizing GQS sprint metadata...")
    run_command(["git", "add", "."])
    commit_msg = f"docs: graduate {len(slugs_to_audit)} nodes to platinum ({', '.join(slugs_to_audit)})"
    if committed_savepoint:
        code, _, _ = run_command(["git", "commit", "--amend", "-m", commit_msg])
    else:
        code, _, _ = run_command(["git", "commit", "-m", commit_msg])
        
    if code == 0:
        print("\033[92m✓ Git transaction committed successfully.\033[0m")
    
    # 6. Refill queue and display status
    print("\n🤖 Replenishing GQS Stack depth...")
    run_command([".venv/bin/python3", "gqs.py", "refill"])
    
    print_banner("SPRINT GRADUATION COMPLETED SUCCESSFULLY", "92")
    subprocess.run([".venv/bin/python3", "gqs.py", "status"])

if __name__ == "__main__":
    main()
