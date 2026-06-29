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
from pydantic import BaseModel, Field

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
            "parents": [parent_hub],
            "identities": [
                {
                    "id": item["identity"]["id"],
                    "title": identity_title,
                    "equation": identity_eq,
                    "description": item["identity"].get("description", "")
                }
            ]
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

def extract_latex_from_svg(svg_string: str) -> str:
    import re, html
    match = re.search(r'data-tex="([^"]+)"', svg_string)
    if match:
        return html.unescape(match.group(1))
    return ""

def formula_status():
    import glob
    shards_dir = "app/config/content/formulas"
    shard_files = glob.glob(os.path.join(shards_dir, "shard_*.json"))
    shard_files.sort()
    
    total = 0
    pending = []
    
    for filepath in shard_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                continue
            for f_id, formula in data.items():
                total += 1
                if formula.get("interpretation") in ["Analysis pending.", "Analysis pending"]:
                    pending.append({
                        "id": f_id,
                        "title": formula.get("title", "Unknown"),
                        "shard": os.path.basename(filepath)
                    })
                    
    enriched = total - len(pending)
    pct = (enriched / total * 100) if total > 0 else 100.0
    
    print("=" * 80)
    print("🪐 PHYSICS LAB: FORMULA REGISTRY STATUS".center(80))
    print("=" * 80)
    print(f"  * Total Formulas:  {total}")
    print(f"  * Enriched:        {enriched} ({pct:.2f}%)")
    print(f"  * Pending (Placeholder): {len(pending)} ({100.0 - pct:.2f}%)")
    
    if pending:
        print("\n📌 NEXT PENDING FORMULAS TO ENRICH:")
        pending.sort(key=lambda x: x["id"])
        for i, item in enumerate(pending[:5]):
            print(f"  {i+1:02d}. \033[1m{item['id']}\033[0m ({item['title']})")
            print(f"      Shard: {item['shard']}")
    else:
        print("\n🎉 All formulas have been successfully enriched!")
    print("=" * 80)

def generate_formula_template(num_items=5):
    import glob
    shards_dir = "app/config/content/formulas"
    shard_files = glob.glob(os.path.join(shards_dir, "shard_*.json"))
    shard_files.sort()
    
    pending = []
    for filepath in shard_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                continue
            for f_id, formula in data.items():
                if formula.get("interpretation") in ["Analysis pending.", "Analysis pending"]:
                    pending.append((f_id, formula))
                    
    if not pending:
        print("Notice: No pending formulas found in the registry to scaffold.")
        return
        
    pending.sort(key=lambda x: x[0])
    
    payload_path = "subfiles/formula_payload.json"
    payload = {}
    if os.path.exists(payload_path):
        try:
            with open(payload_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except Exception:
            payload = {}
            
    scaffolded_ids = []
    
    for f_id, formula in pending[:num_items]:
        if f_id in payload:
            continue
        latex_src = extract_latex_from_svg(formula.get("equation", ""))
        
        payload[f_id] = {
            "title": formula.get("title", "Unknown Formula"),
            "equation_svg": formula.get("equation", ""),
            "latex": latex_src,
            "conceptual_definition": "[AI-DRAFT: A high-level conceptual explanation of what this physics formula represents.]",
            "intuitive_summary": "[AI-DRAFT: A concise, single-sentence summary of the physical intuition behind the equation.]",
            "interpretation": "[AI-DRAFT: A paragraph explaining the role of variables in the equation and their physical relationships.]",
            "symmetry_origin": "[AI-DRAFT: The coordinate invariance, conservation law, or physical derivation origin.]",
            "limits_and_boundary": "[AI-DRAFT: Asymptotic limits when variables approach zero or infinity.]",
            "semantic_variables": {
                "[symbol]": {
                    "name": "[AI-DRAFT: Physical name]",
                    "type": "variable",
                    "unit": "[SI units]",
                    "description": "[AI-DRAFT: Detailed explanation]"
                }
            }
        }
        scaffolded_ids.append(f_id)
        
    if not scaffolded_ids:
        print("Notice: All of the next pending formulas are already scaffolded in the payload.")
        return
        
    with open(payload_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
        
    print(f"✓ SUCCESS: Scaffolded {len(scaffolded_ids)} formula entries in {payload_path}:")
    for f_id in scaffolded_ids:
        print(f"  * \033[1m{f_id}\033[0m ({payload[f_id]['title']})")
    print("\n👉 Open subfiles/formula_payload.json and replace the placeholders with rich academic definitions,")
    print("   or ask me (Antigravity) to draft them for you using the platform model.")

def ingest_formulas():
    import glob, hashlib, tempfile
    payload_path = "subfiles/formula_payload.json"
    if not os.path.exists(payload_path):
        print(f"Error: Ingestion payload not found at {payload_path}")
        return
        
    with open(payload_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        
    if not payload:
        print("Notice: Formula payload is empty. Nothing to ingest.")
        return
        
    has_scaffold = False
    for f_id, data in payload.items():
        if any("[AI-DRAFT" in str(v) for v in data.values()) or any("[AI-DRAFT" in str(v) for v in data.get("semantic_variables", {}).values()):
            has_scaffold = True
            break
            
    if has_scaffold:
        print("\033[91m⚠️ WARNING: The formula payload contains unprocessed placeholders!\033[0m")
        print("Please replace all bracketed instructions in subfiles/formula_payload.json with definitions before ingesting.")
        confirm = input("Are you sure you want to proceed? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            return

    print("🚀 Ingesting formula definitions into local JSON shards...")
    shards_dir = "app/config/content/formulas"
    
    shards_updated = set()
    
    for f_id, draft in payload.items():
        hex_prefix = hashlib.md5(f_id.encode('utf-8')).hexdigest()[:2]
        shard_path = os.path.join(shards_dir, f"shard_{hex_prefix}.json")
        
        if not os.path.exists(shard_path):
            print(f"  ⚠️ Error: Shard file does not exist: {shard_path} for formula '{f_id}'")
            continue
            
        with open(shard_path, 'r', encoding='utf-8') as f:
            try:
                shard_data = json.load(f)
            except Exception as e:
                print(f"  ⚠️ Error loading shard {shard_path}: {e}")
                continue
                
        if f_id not in shard_data:
            print(f"  ⚠️ Error: Formula '{f_id}' not found in target shard {shard_path}")
            continue
            
        formula = shard_data[f_id]
        
        formula["conceptual_definition"] = draft.get("conceptual_definition", "")
        formula["intuitive_summary"] = draft.get("intuitive_summary", "")
        formula["interpretation"] = draft.get("interpretation", "")
        formula["symmetry_origin"] = draft.get("symmetry_origin", "")
        formula["limits_and_boundary"] = draft.get("limits_and_boundary", "")
        
        sem_vars = {}
        for sym, v_data in draft.get("semantic_variables", {}).items():
            if sym == "[symbol]" or "[AI-DRAFT" in str(v_data):
                continue
            sem_vars[sym] = {
                "name": v_data.get("name", sym),
                "type": v_data.get("type", "variable"),
                "unit": v_data.get("unit", "dimensionless"),
                "description": v_data.get("description", "")
            }
        formula["semantic_variables"] = sem_vars
        
        temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(shard_path))
        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(shard_data, f, indent=4, ensure_ascii=False)
            os.replace(temp_path, shard_path)
            shards_updated.add(shard_path)
            print(f"  ✓ Updated formula '{f_id}' in {os.path.basename(shard_path)}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"  ⚠️ Error saving shard {shard_path}: {e}")
            
    with open(payload_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, indent=4)
        
    print(f"\n✓ SUCCESS: Ingested drafts and updated {len(shards_updated)} shard files.")
    
    print("\n🔄 Synchronizing database tables...")
    try:
        subprocess.run(["php", "cli_sync.php"])
        print("✓ Database table sync completed.")
    except Exception as e:
        print(f"  ⚠️ Database sync failed: {e}")

# Define Pydantic Schema for Structured Output at Global Scope
class SemanticVariable(BaseModel):
    symbol: str = Field(description="The mathematical symbol of the variable as it appears in the equation (e.g. F_g, m_1, r).")
    name: str = Field(description="The physical name of the variable (e.g. First Mass).")
    type: str = Field(description="Whether it is a variable parameter or physical constant (must be 'variable' or 'constant').")
    unit: str = Field(description="The SI units of the variable (e.g., kg, m/s).")
    description: str = Field(description="Detailed explanation of what this variable represents in this context.")

class PhysicsFormulaMetadata(BaseModel):
    conceptual_definition: str = Field(description="A high-level conceptual explanation of what this physics formula represents.")
    intuitive_summary: str = Field(description="A concise, single-sentence summary of the physical intuition behind the equation.")
    interpretation: str = Field(description="A paragraph explaining the role of variables in the equation and their physical relationships.")
    symmetry_origin: str = Field(description="The coordinate invariance, conservation law, or physical derivation origin.")
    limits_and_boundary: str = Field(description="Asymptotic limits when variables approach zero or infinity.")
    semantic_variables: list[SemanticVariable] = Field(description="List of all mathematical variables in the formula.")

def seed(rate_tier="free"):
    """Enrich empty/placeholder formula entries across the 256 JSON shards using the Gemini API.
    Uses the modern google-genai SDK and secure Keychain API key retrieval.
    """
    import glob
    import re
    import html
    import time
    import keyring
    import os
    import tempfile
    
    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import APIError
    except ImportError:
        print("Error: The 'google-genai' package is not installed in the virtual environment.")
        print("Please run: .venv/bin/python3 -m pip install google-genai")
        sys.exit(1)

    # Parse rate tier or custom cooldown
    cooldown = 4.5  # Default safe delay for Free Tier (approx 13 RPM, limit is 15 RPM)
    try:
        cooldown = float(rate_tier)
    except ValueError:
        if rate_tier in ["paid", "pay", "unlimited"]:
            cooldown = 0.2
            print("Using paid/high-throughput rate tier (0.2s cooldown per request).")
        else:
            print(f"Using default free rate tier (4.5s cooldown per request).")

    # 1. Configure Gemini API Client
    print("Retrieving API key from Keychain...", flush=True)
    api_key = keyring.get_password("physics_lab", "gemini_api_key")
    if not api_key:
        print("Error: Gemini API key not found in your OS Keychain.")
        print("Please store your key in the keychain first by running:")
        print("  .venv/bin/keyring set physics_lab gemini_api_key")
        sys.exit(1)
    print("API key successfully retrieved.", flush=True)

    client = genai.Client(api_key=api_key)
    MODEL_NAME = 'gemini-3.5-flash'
    SHARDS_DIR = "app/config/content/formulas"

    def extract_latex_from_svg(svg_string: str) -> str:
        match = re.search(r'data-tex="([^"]+)"', svg_string)
        if match:
            return html.unescape(match.group(1))
        return ""

    def process_shard(filepath: str):
        print(f"Checking shard: {os.path.basename(filepath)}...", flush=True)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                shard_data = json.load(f)
            except Exception as e:
                print(f"Error loading {os.path.basename(filepath)}: {e}", flush=True)
                return
        
        updated = False
        
        for formula_id, formula in shard_data.items():
            if formula.get("interpretation") in ["Analysis pending.", "Analysis pending"]:
                title = formula.get("title", "Unknown Formula")
                svg_eq = formula.get("equation", "")
                latex_src = extract_latex_from_svg(svg_eq)
                
                if not latex_src:
                    print(f"  Skipping '{title}' (Unable to parse LaTeX from SVG)", flush=True)
                    continue
                    
                print(f"  -> Seeding missing definition for: '{title}'...", flush=True)
                
                prompt = f"""
                You are an expert physics professor and digital encyclopedia curator. 
                Author a detailed explanation of the physics formula:
                Title: {title}
                LaTeX Equation: {latex_src}
                
                Follow these constraints:
                1. Keep descriptions clear, mathematically rigorous, and educational.
                2. Format any variables in text descriptions with LaTeX inline delimiters: \\( variable \\).
                3. Ensure SI units in variables are standard (e.g. kg, m/s^2, J).
                """
                
                # Call Gemini API with retries
                max_retries = 3
                backoff_delay = 10.0
                response = None
                
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=PhysicsFormulaMetadata
                            )
                        )
                        break
                    except APIError as e:
                        if e.code in [429, 503]:
                            print(f"    Temporary error {e.code} (attempt {attempt + 1}/{max_retries}). Sleeping for {backoff_delay} seconds...", flush=True)
                            time.sleep(backoff_delay)
                            backoff_delay *= 2
                        else:
                            print(f"    API Error generating content for '{title}': {e}", flush=True)
                            break
                    except Exception as e:
                        print(f"    General Error generating content for '{title}': {e}", flush=True)
                        break
                
                if response is None:
                    print(f"    Skipping '{title}' due to persistent API errors. Cooling down for 5.0 seconds...", flush=True)
                    time.sleep(5.0)
                    continue
                    
                try:
                    meta = json.loads(response.text)
                    vars_list = meta.get("semantic_variables", [])
                    vars_dict = {}
                    for v in vars_list:
                        symbol = v.get("symbol")
                        if symbol:
                            vars_dict[symbol] = {
                                "name": v.get("name", symbol),
                                "type": v.get("type", "variable"),
                                "unit": v.get("unit", "dimensionless"),
                                "description": v.get("description", "")
                            }
                    
                    formula["conceptual_definition"] = meta.get("conceptual_definition", "Conceptual definition pending.")
                    formula["intuitive_summary"] = meta.get("intuitive_summary", "Intuitive summary pending.")
                    formula["interpretation"] = meta.get("interpretation", "Analysis pending.")
                    formula["symmetry_origin"] = meta.get("symmetry_origin", "Theoretical origin under investigation.")
                    formula["limits_and_boundary"] = meta.get("limits_and_boundary", "Boundary conditions pending.")
                    formula["semantic_variables"] = vars_dict
                    
                    updated = True
                    print(f"    Success: Enriched metadata for '{title}'", flush=True)
                    time.sleep(cooldown)
                except Exception as e:
                    print(f"    Error parsing generated content for '{title}': {e}", flush=True)
                    time.sleep(cooldown)
                    
        if updated:
            temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
            try:
                with open(temp_fd, 'w', encoding='utf-8') as f:
                    json.dump(shard_data, f, indent=4, ensure_ascii=False)
                os.replace(temp_path, filepath)
                print(f"  Saved changes to {os.path.basename(filepath)}", flush=True)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"  Error saving changes to {os.path.basename(filepath)}: {e}", flush=True)

    # Find all shards
    shard_files = glob.glob(os.path.join(SHARDS_DIR, "shard_*.json"))
    shard_files.sort()
    
    if not shard_files:
        print(f"No formula JSON shards found in {SHARDS_DIR}", flush=True)
        return
        
    print(f"Found {len(shard_files)} shards. Commencing GQS Database Seeding...", flush=True)
    for filepath in shard_files:
        process_shard(filepath)
    print("Database seeding completed.", flush=True)

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
    elif cmd == "seed":
        rate_tier = sys.argv[2] if len(sys.argv) > 2 else "free"
        seed(rate_tier)
    elif cmd == "formula-status":
        formula_status()
    elif cmd == "formula-template":
        num = 5
        if len(sys.argv) > 2:
            try:
                num = int(sys.argv[2])
            except ValueError:
                pass
        generate_formula_template(num)
    elif cmd == "formula-ingest":
        ingest_formulas()
    else:
        print(f"Unknown command '{cmd}'. Available commands:")
        print("  status            Display database status and next stack queue items (Default)")
        print("  template [N]      Scaffold the next N items into subfiles/batch_payload.json")
        print("  ingest            Graduate all drafted subtopics from subfiles/batch_payload.json")
        print("  audit [slug]      Run structural and formula validation audits")
        print("  refill [N]        Replenish GQS stack depth and sync expansion sprint")
        print("  seed              Enrich missing formula/identity definitions using the Gemini API")
        print("  formula-status    Display live status of formula registry and pending placeholders")
        print("  formula-template  Scaffold the next N pending formulas into subfiles/formula_payload.json")
        print("  formula-ingest    Graduate completed formula drafts from subfiles/formula_payload.json")
        sys.exit(1)

if __name__ == "__main__":
    main()
