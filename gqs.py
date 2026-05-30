#!/usr/bin/env python3
"""
🪐 Physics Lab - Graduation Queue Stack (GQS) CLI Control Center
Unified session control, backlog synchronization, automated templating, and compilation.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# Paths
GQS_PATH = "subfiles/graduation_queue_stack.json"
PAYLOAD_PATH = "subfiles/batch_payload.json"
ACTIVE_SPRINT_PATH = "subfiles/active_expansion_sprint.json"
HEALTH_PATH = "system_health.json"


def print_quality_breakdown(health_path=HEALTH_PATH):
    """Surface the platinum classification + qualitative violations from
    system_health.json so users see both the CTA-aligned (flagged) count
    and the strict (organic) count in one place. Silent no-op if the
    file is missing or malformed — the CTA dashboard above is the
    authoritative live source.
    """
    if not os.path.exists(health_path):
        return
    try:
        with open(health_path) as f:
            health = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    sc = health.get("platinum_scorecard")
    if not sc:
        return

    integrity = health.get("integrity_summary", {})
    last = health.get("last_updated", "unknown")

    flagged = sc.get("flagged_platinum_count", 0)
    flagged_pct = sc.get("flagged_platinum_percentage", 0)
    organic = sc.get("organic_platinum_count", 0)
    organic_pct = sc.get("organic_platinum_percentage", 0)
    flag_viol = sc.get("flag_violations", 0)
    pseudo = sc.get("pseudo_platinum_count", 0)

    print()
    print("=" * 80)
    print(f" QUALITY BREAKDOWN (system_health.json @ {last}) ".center(80, "="))
    print("=" * 80)
    print("  PLATINUM CLASSIFICATION:")
    print(f"    \033[92mFlagged (CTA-aligned):    {flagged:>4}\033[0m  ({flagged_pct}%)  -- standard == \"platinum\" on disk")
    print(f"    \033[92mOrganic (strict):         {organic:>4}\033[0m  ({organic_pct}%)  -- flagged + passes qualitative gates")
    print(f"    \033[93mFlag violations:          {flag_viol:>4}\033[0m            -- flagged but fails lead/artifact")
    print(f"    \033[93mPseudo-platinum:          {pseudo:>4}\033[0m            -- meets quant but not flagged")
    print()
    print("  QUALITATIVE VIOLATIONS:")
    print(f"    Lead-rule (In Media Res):    {sc.get('lead_violations', 0)}")
    print(f"    Artifact (lists/bullets):    {sc.get('artifact_violations', 0)}")
    print(f"    Low depth (<650 words):      {sc.get('low_depth_count', 0)}")
    print(f"    Non-technical density:       {sc.get('non_technical_count', 0)}")
    print()
    print("  INTEGRITY SUMMARY:")
    print(f"    Broken links:         {integrity.get('broken_links', 0)}")
    print(f"    Broken formulas:      {integrity.get('broken_formulas', 0)}")
    print(f"    Orphans (no inbound): {integrity.get('orphans_count', 0)}")
    print("=" * 80)


def show_status():
    print("=" * 80)
    print("🪐 PHYSICS LAB: GRADUATION QUEUE STACK (GQS) CLI".center(80))
    print("=" * 80)
    
    # 1. Sync backlog and show CTA dashboard
    print("🤖 Synchronizing backlog and auditing database...")
    subprocess.run([".venv/bin/python3", "scripts/maintenance/sync_backlog.py"])

    # 1b. Surface platinum classification (flagged vs organic) + violations
    print_quality_breakdown()

    # 2. Read GQS Stack
    if os.path.exists(GQS_PATH):
        with open(GQS_PATH, "r") as f:
            stack = json.load(f)
        pending = [item for item in stack if item.get("status", "pending") == "pending"]
        print(f"\n⚡ GQS Stack Depth: {len(stack)} total ({len(pending)} pending backlog items)")
        if pending:
            print("\n📌 NEXT QUEUE TARGETS:")
            for i, item in enumerate(pending[:3]):
                print(f"  {i+1:02d}. \033[1m{item['slug']}\033[0m ({item['title']})")
                print(f"      Shard: {item['shard']} | Paragraphs Target: {item['paragraphs']}")
                print(f"      Identity: {item['identity']['title']} (ID: {item['identity']['id']})")
        else:
            print("  Notice: No pending items in the stack. Run 'refill' to replenish.")
    else:
        print("\n⚠️ GQS Stack not found. Run 'refill' to initialize.")

    # 3. Check draft payload status
    if os.path.exists(PAYLOAD_PATH):
        try:
            with open(PAYLOAD_PATH, "r") as f:
                payload = json.load(f)
            if payload:
                print(f"\n📝 ACTIVE INGESTION DRAFTS in {PAYLOAD_PATH}:")
                for slug, data in payload.items():
                    content = data.get("content", "")
                    words = len(content.split())
                    is_scaffolded = "Paragraph" in content and "OPS" in content
                    status = "\033[93mSCAFFOLDED (Pending Prose Writing)\033[0m" if is_scaffolded else "\033[92mDRAFTED (Ready for Ingestion)\033[0m"
                    print(f"  * \033[1m{slug}\033[0m [{status}] (~{words} words)")
                print("\n👉 To graduate these drafts, run:")
                print("   \033[1m.venv/bin/python3 gqs.py ingest\033[0m")
            else:
                print(f"\n📝 Ingestion payload {PAYLOAD_PATH} is empty.")
                print("👉 To scaffold the next target, run:")
                print("   \033[1m.venv/bin/python3 gqs.py template 1\033[0m")
        except Exception:
            print(f"\n⚠️ Error reading payload at {PAYLOAD_PATH}")
    else:
        print(f"\n📝 Ingestion payload {PAYLOAD_PATH} does not exist.")
        print("👉 To scaffold the next target, run:")
        print("   \033[1m.venv/bin/python3 gqs.py template 1\033[0m")
    
    print("\n" + "=" * 80)

def generate_template(num_items=1):
    if not os.path.exists(GQS_PATH):
        print(f"Error: GQS stack not found at {GQS_PATH}. Run 'refill' first.")
        sys.exit(1)
        
    with open(GQS_PATH, "r") as f:
        stack = json.load(f)
        
    pending_items = [item for item in stack if item.get("status", "pending") == "pending"]
    if not pending_items:
        print("Notice: No pending backlog items in stack to scaffold.")
        return

    payload = {}
    if os.path.exists(PAYLOAD_PATH):
        try:
            with open(PAYLOAD_PATH, "r") as f:
                payload = json.load(f)
        except Exception:
            payload = {}

    scaffolded_slugs = []
    
    for item in pending_items[:num_items]:
        slug = item["slug"]
        title = item["title"]
        shard = item["shard"]
        paragraphs = item["paragraphs"]
        neighbors = [n["title"] for n in item["neighbors"]]
        bridge_title = item["bridge"]["title"]
        identity_title = item["identity"]["title"]
        identity_eq = item["identity"]["equation"]
        
        # Parent hub resolution
        parent_hub = shard.replace(".json", "")
        
        # Distribute neighbor terms across paragraphs organically
        # We avoid putting them all in Paragraph 1, and we avoid the final paragraph (limiting case).
        # We also avoid Paragraph 2 if possible to keep the math identity focused.
        eligible_p_indices = [1] + [i for i in range(3, paragraphs)]
        if not eligible_p_indices:
            eligible_p_indices = [1]
            
        p_neighbors = {i: [] for i in range(1, paragraphs + 1)}
        for idx, n_title in enumerate(neighbors):
            p_idx = eligible_p_indices[idx % len(eligible_p_indices)]
            p_neighbors[p_idx].append(n_title)
        
        # Fully unconstrained dynamic allocation across the entire range [1, paragraphs]
        # This eliminates the Paragraph 3 clustering bottleneck while maintaining zero overlap.
        slug_hash = sum(ord(c) for c in slug)
        math_p_index = 1 + (slug_hash % paragraphs)
        bridge_p_index = 2 if math_p_index != 2 else 3
        
        # Build paragraph templates
        p_list = []
        for i in range(1, paragraphs + 1):
            if i == 1:
                n_list = p_neighbors[1]
                n_text = f" Bold the first mention of neighbor terms using <strong>[Term]</strong>: {', '.join(n_list)}." if n_list else ""
                p_text = (
                    f"Paragraph 1/{paragraphs} (OPS In-Media-Res Lead): Start directly with a physical principle, identity, or derivation. "
                    f"DO NOT start with 'The {title} is...' or 'This concept refers to...'. "
                    f"DO NOT mention the title '{title}' in the first 15 words of the paragraph.{n_text}"
                )
            elif i == paragraphs:
                n_list = p_neighbors[i]
                n_text = f" Bold the first mention of neighbor terms using <strong>[Term]</strong>: {', '.join(n_list)}." if n_list else ""
                p_text = (
                    f"Paragraph {i}/{paragraphs} (OPS Limiting Case & Closure): Mathematically or conceptually demonstrate the Limiting Case of this concept "
                    f"(e.g., how this reduces to a classical or simpler regime). "
                    f"DO NOT use formulaic lead-ins like 'The limiting case of...'. "
                    f"Ensure the total word count across all paragraphs is strictly between 650 to 1,000 words of dense, university-level prose. "
                    f"Ensure continuous prose with zero bullet lists or numbered items.{n_text}"
                )
            else:
                p_text = f"Paragraph {i}/{paragraphs}: Technical expansion on the physical/mathematical framework."
                n_list = p_neighbors[i]
                if n_list:
                    p_text += f" Bold the first mention of neighbor terms using <strong>[Term]</strong>: {', '.join(n_list)}."
            
            # Append dynamic identity and bridge locks to ANY paragraph index (including 1 and N)
            if i == math_p_index:
                p_text += (
                    f" Integrate the key mathematical identity lock: {identity_title} in a centered display math block, "
                    f"written mathematically as <div class=\"math-display\" style=\"text-align: center; margin: 25px 0;\">\\\\[ {identity_eq} \\\\]</div>. "
                    f"CRITICAL: Weave the equation organically; DO NOT introduce it using formulaic phrases like 'written mathematically as' "
                    f"and DO NOT follow it with a glossary-style list starting with 'where [symbol] is...'."
                )
            if i == bridge_p_index:
                p_text += f" Establish the cross-hub connectivity bridge to the topic of {bridge_title}."
            
            p_list.append(f"<p>[{p_text}]</p>")
            
        payload[slug] = {
            "title": title,
            "content": "".join(p_list),
            "standard": "platinum",
            "parents": [parent_hub]
        }
        scaffolded_slugs.append(slug)

    with open(PAYLOAD_PATH, "w") as f:
        json.dump(payload, f, indent=4)
        
    print(f"✓ SUCCESS: Scaffolded {len(scaffolded_slugs)} template entries in {PAYLOAD_PATH}:")
    for s in scaffolded_slugs:
        print(f"  * \033[1m{s}\033[0m")
    print("\n👉 Open subfiles/batch_payload.json and replace the bracketed instructions with rich academic prose!")

def ingest():
    if not os.path.exists(PAYLOAD_PATH):
        print(f"Error: Payload file not found at {PAYLOAD_PATH}")
        sys.exit(1)
        
    with open(PAYLOAD_PATH, "r") as f:
        payload = json.load(f)
        
    if not payload:
        print("Notice: Payload file is empty. Nothing to ingest.")
        return

    # Check if we still have unresolved scaffold tags
    has_scaffold = any("Paragraph" in data.get("content", "") and "OPS" in data.get("content", "") for data in payload.values())
    if has_scaffold:
        print("\033[91m⚠️ WARNING: The payload contains unprocessed template placeholders!\033[0m")
        print("Please replace all bracketed instructions in subfiles/batch_payload.json with your written prose before ingesting.")
        confirm = input("Are you sure you want to proceed? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            sys.exit(0)

    print("🚀 Invoking GQS Batch Ingest Subprocess...")
    subprocess.run([".venv/bin/python3", "scripts/maintenance/batch_ingest.py"])
    
    # Clean up the payload file so it starts fresh next time
    if os.path.exists(PAYLOAD_PATH):
        with open(PAYLOAD_PATH, "w") as f:
            json.dump({}, f, indent=4)
        print(f"✓ SUCCESS: Cleaned up {PAYLOAD_PATH} after successful graduation.")

def audit(slug=None):
    cmd = [".venv/bin/python3", "integrity_shield.py"]
    if slug:
        cmd.append(slug)
        print(f"🛡️ Running single-node audit for: {slug}...")
    else:
        print("🛡️ Running full sitewide integrity audit...")
    subprocess.run(cmd)

def refill(limit=30):
    print(f"🔄 Replenishing central GQS queue stack (Target depth: {limit})...")
    subprocess.run([".venv/bin/python3", "scripts/maintenance/generate_sprint_queue.py", str(limit)])

def main():
    if len(sys.argv) < 2:
        show_status()
        sys.exit(0)
        
    cmd = sys.argv[1].lower()
    
    if cmd == "status":
        show_status()
    elif cmd == "template":
        num = 1
        if len(sys.argv) > 2:
            try:
                num = int(sys.argv[2])
            except ValueError:
                pass
        generate_template(num)
    elif cmd == "ingest":
        ingest()
    elif cmd == "audit":
        slug = sys.argv[2] if len(sys.argv) > 2 else None
        audit(slug)
    elif cmd == "refill":
        limit = 30
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                pass
        refill(limit)
    else:
        print(f"Unknown command '{cmd}'. Available commands:")
        print("  status        Display database status and next stack queue items (Default)")
        print("  template [N]  Scaffold the next N items into subfiles/batch_payload.json")
        print("  ingest        Graduate all drafted subtopics from subfiles/batch_payload.json")
        print("  audit [slug]  Run structural and formula validation audits")
        print("  refill [N]    Replenish GQS stack depth and sync expansion sprint")
        sys.exit(1)

if __name__ == "__main__":
    main()
