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

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
        
    sem_ref_path = "app/config/ref_data/semantic_references.json"
    sem_refs = {}
    if os.path.exists(sem_ref_path):
        try:
            with open(sem_ref_path, "r") as f:
                sem_refs = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load semantic references: {e}")
        
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
        
        # Resolve target keywords from semantic references
        sem_keywords = sem_refs.get(slug, {}).get("keywords", [])
        
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
                k_text = f" Mandatory Semantic Keywords to integrate in the prose to pass OPS verification: {', '.join(sem_keywords)}." if sem_keywords else ""
                p_text = (
                    f"Paragraph 1/{paragraphs} (OPS In-Media-Res Lead): Start directly with a physical principle, identity, or derivation. "
                    f"DO NOT start with 'The {title} is...' or 'This concept refers to...'. "
                    f"DO NOT mention the title '{title}' in the first 15 words of the paragraph.{n_text}{k_text}"
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
    if not svg_string:
        return ""
    val = svg_string.strip()
    if not val.startswith("<svg"):
        if val.startswith("\\[") and val.endswith("\\]"):
            val = val[2:-2].strip()
        return val

    # Fallbacks for SVGs missing data-tex attributes
    if "cyclic-conservation-law" in val:
        return r"\frac{\partial L}{\partial q_k} = 0 \implies \frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_k}\right) = 0 \implies p_k = C"
    if "maxwell-faraday-law" in val or "faradays-law" in val:
        return r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}"
    if "generalized-momentum-identity" in val:
        return r"p_k = \frac{\partial L}{\partial \dot{q}^k}"
    if "bayesian-probabilistic-failure" in val:
        return r"P(T|S) = \frac{P(S|T)P(T)}{P(S)}"
    if "crystal-math" in val:
        return r"\lambda = \frac{h}{\sqrt{2m_e eV}} \approx 1.7 \text{ \AA}"

    match = re.search(r'data-tex="([^"]+)"', svg_string)
    if match:
        return html.unescape(match.group(1))
    return ""

def is_formula_pending(formula):
    import re
    placeholders = [
        "derivation pending", "analysis pending", 
        "no interpretation provided", "symmetry derivation pending",
        "limiting case pending", "boundary conditions pending", 
        "theoretical origin under investigation.", "analysis pending.",
        "great expansion: symmetry derivation pending.",
        "great expansion: limiting case analysis pending."
    ]
    for field in ["conceptual_definition", "intuitive_summary", "interpretation", "symmetry_origin", "limits_and_boundary"]:
        val = str(formula.get(field, "")).strip().lower()
        if not val:
            return True
        if any(p in val for p in placeholders):
            return True
        if re.search(r'\bpending\b', val):
            return True
    return False

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
                if is_formula_pending(formula):
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
                if is_formula_pending(formula):
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
    
    print("\n🎨 Pre-rendering formulas into SVGs...")
    try:
        subprocess.run(["python3", "scratch/compile_formulas.py"])
        print("✓ Formulas compiled to SVG.")
    except Exception as e:
        print(f"  ⚠️ Compilation failed: {e}")

    print("\n🔄 Synchronizing database tables...")
    try:
        subprocess.run(["php", "cli_sync.php"])
        print("✓ Database table sync completed.")
    except Exception as e:
        print(f"  ⚠️ Database sync failed: {e}")

class FormulaNaming(BaseModel):
    latex: str = Field(description="The input LaTeX equation.")
    title: str = Field(description="Standard physical title of the formula.")
    id: str = Field(description="Clean lowercase alphanumeric slug/ID for the formula using hyphens (e.g. fundamental-thermodynamic-relation).")

class FormulaNamingList(BaseModel):
    namings: list[FormulaNaming]

def clean_latex(latex_str):
    import re, html
    val = latex_str.strip()
    val = html.unescape(val)
    val = re.sub(r"^(\\\[|\\\(|\$\$|\$)", "", val)
    val = re.sub(r"(\\\]|\\\)||\$\$|\$)$", "", val)
    val = re.sub(r"\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^}]+)\}", r"\2", val)
    val = re.sub(r"\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])", r"\2", val)
    val = re.sub(r"_\{[^}]+\}", "", val)
    val = re.sub(r"_[a-zA-Z0-9]", "", val)
    val = re.sub(r"[^a-zA-Z0-9_\^\\=+\/\*\(\)\[\]<>\.,;?-]", "", val)
    return val.lower().strip()

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
    Supports Vertex AI (GCP credits) and concurrent parallel execution.
    """
    import glob
    import re
    import html
    import time
    import threading
    import keyring
    import os
    import tempfile
    import socket
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Prevent infinite hangs on network sockets
    socket.setdefaulttimeout(30.0)
    
    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import APIError
    except ImportError:
        print("Error: The 'google-genai' package is not installed in the virtual environment.")
        print("Please run: .venv/bin/python3 -m pip install google-genai")
        sys.exit(1)

    # Parse rate tier or custom cooldown
    cooldown = 5.0  # Default safe delay for Free Tier (approx 12 RPM, limit is 15 RPM)
    try:
        cooldown = float(rate_tier)
    except ValueError:
        if rate_tier in ["paid", "pay", "unlimited"]:
            cooldown = 0.2
            print("Using paid/high-throughput rate tier (0.2s cooldown per request).")
        else:
            print(f"Using default free rate tier (5.0s cooldown per request).")

    # 1. Configure Gemini API Client (AI Studio vs Vertex AI)
    api_key = os.environ.get("GEMINI_API_KEY") or keyring.get_password("physics_lab", "gemini_api_key")
    gcp_project = os.environ.get("GCP_PROJECT_ID")
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    is_vertex = bool(gcp_project and credentials_path)

    if is_vertex:
        print(f"Initializing Vertex AI client for project: {gcp_project}", flush=True)
        client = genai.Client(
            vertexai=True,
            project=gcp_project,
            location="us-central1",
            http_options=types.HttpOptions(timeout=30_000)
        )
        MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-flash-lite")
        print(f"Using Vertex AI Model: {MODEL_NAME}", flush=True)
    else:
        if not api_key:
            print("Error: No GEMINI_API_KEY found in environment or keyring.", flush=True)
            sys.exit(1)
        print("API key successfully retrieved.", flush=True)
        if api_key.startswith("AQ.") or api_key.startswith("ya29."):
            from google.oauth2.credentials import Credentials
            client = genai.Client(credentials=Credentials(token=api_key), http_options=types.HttpOptions(timeout=30_000))
        else:
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30_000))
        MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-flash-latest")
        print(f"Using Google AI Studio Model: {MODEL_NAME}", flush=True)

    SHARDS_DIR = "app/config/content/formulas"
    consecutive_429s = [0]

    # Determine Concurrency
    concurrency = 1
    if is_vertex or rate_tier in ["paid", "pay", "unlimited", "vertex"]:
        concurrency = 10
        cooldown = 0.0
        print(f"Enabling parallel seeding with {concurrency} concurrent workers (cooldown: 0s).", flush=True)
    else:
        print(f"Running sequentially (cooldown: {cooldown}s).", flush=True)


    def save_shard_file(filepath, shard_data):
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

    def process_shard(filepath: str):
        print(f"Checking shard: {os.path.basename(filepath)}...", flush=True)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                shard_data = json.load(f)
            except Exception as e:
                print(f"Error loading {os.path.basename(filepath)}: {e}", flush=True)
                return

        pending_items = []
        for formula_id, formula in shard_data.items():
            if is_formula_pending(formula):
                pending_items.append((formula_id, formula))

        if not pending_items:
            return

        print(f"Found {len(pending_items)} pending formulas in {os.path.basename(filepath)}.", flush=True)
        shard_updated = [False]
        write_lock = threading.Lock()

        def seed_formula(formula_id, formula):
            title = formula.get("title", "Unknown Formula")
            svg_eq = formula.get("equation", "")
            latex_src = extract_latex_from_svg(svg_eq)

            if not latex_src:
                print(f"  Skipping '{title}' (Unable to parse LaTeX from SVG)", flush=True)
                return

            print(f"  -> Seeding: '{title}'...", flush=True)

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

            max_retries = 3
            backoff_delay = 10.0
            response = None
            rate_limit_hit = False

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
                        print(f"    Temporary error {e.code} for '{title}': {e} (attempt {attempt + 1}/{max_retries}). Sleeping...", flush=True)
                        time.sleep(backoff_delay)
                        backoff_delay *= 2
                        if e.code == 429:
                            rate_limit_hit = True
                    else:
                        print(f"    API Error generating content for '{title}': {e}", flush=True)
                        break
                except Exception as e:
                    print(f"    General Error generating content for '{title}': {e}", flush=True)
                    break

            if not response or not response.text:
                if rate_limit_hit:
                    consecutive_429s[0] += 1
                    print(f"    Skipping '{title}' due to persistent 429 rate limits. (Consecutive 429s: {consecutive_429s[0]})", flush=True)
                    if consecutive_429s[0] >= 3 and not is_vertex and rate_tier not in ["paid", "pay", "unlimited", "vertex"]:
                        print(f"\n🛑 CRITICAL: Encountered 429 RESOURCE_EXHAUSTED 3 times consecutively. Daily free tier limit likely reached. Exiting cleanly.", flush=True)
                        raise Exception("consecutive_429_limit_reached")
                    print("    Sleeping 30 seconds (circuit breaker)...", flush=True)
                    time.sleep(30.0)
                else:
                    consecutive_429s[0] = 0
                    print(f"    Skipping '{title}' due to persistent API errors. Cooling down...", flush=True)
                    time.sleep(5.0)
                return

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

                shard_updated[0] = True
                consecutive_429s[0] = 0
                print(f"    Success: '{title}'", flush=True)
                with write_lock:
                    save_shard_file(filepath, shard_data)
                if cooldown > 0:
                    time.sleep(cooldown)
            except Exception as e:
                consecutive_429s[0] = 0
                print(f"    Error parsing content for '{title}': {e}", flush=True)
                if cooldown > 0:
                    time.sleep(cooldown)

        if concurrency > 1:
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = {executor.submit(seed_formula, fid, f): fid for fid, f in pending_items}
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        if str(e) == "consecutive_429_limit_reached":
                            sys.exit(0)
                        else:
                            print(f"    Error in worker thread: {e}", flush=True)
        else:
            for fid, f in pending_items:
                seed_formula(fid, f)

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

def save_json_atomically(filepath, data):
    import tempfile
    temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
    try:
        with open(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, filepath)
        return True
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"Error saving atomically to {filepath}: {e}")
        return False

def scaffold_to_formula_payload(formula_id: str, formula_data: dict):
    payload_path = "subfiles/formula_payload.json"
    payload = {}
    if os.path.exists(payload_path):
        try:
            with open(payload_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except Exception:
            payload = {}
            
    latex_src = extract_latex_from_svg(formula_data.get("equation", ""))
    
    payload[formula_id] = {
        "title": formula_data.get("title", "Unknown Formula"),
        "equation_svg": formula_data.get("equation", ""),
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
    
    with open(payload_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
    print(f"✓ Scaffolded '{formula_id}' in {payload_path}")

def create_formula_entry(formula_id: str, title: str, latex: str, subtopic_slug: str = None):
    import hashlib
    shards_dir = "app/config/content/formulas"
    hex_prefix = hashlib.md5(formula_id.encode('utf-8')).hexdigest()[:2]
    shard_path = os.path.join(shards_dir, f"shard_{hex_prefix}.json")
    
    shard_data = {}
    if os.path.exists(shard_path):
        with open(shard_path, 'r', encoding='utf-8') as f:
            try:
                shard_data = json.load(f)
            except Exception as e:
                print(f"Error loading shard {shard_path}: {e}")
                return False
                
    if formula_id in shard_data:
        print(f"Error: Formula ID '{formula_id}' already exists in {os.path.basename(shard_path)}.")
        return False
        
    shard_data[formula_id] = {
        "title": title,
        "equation": f"\\[ {latex} \\]",
        "conceptual_definition": "derivation pending",
        "intuitive_summary": "analysis pending",
        "interpretation": "analysis pending",
        "symmetry_origin": "analysis pending",
        "limits_and_boundary": "analysis pending",
        "status": "platinum-draft",
        "semantic_variables": {}
    }
    
    if not save_json_atomically(shard_path, shard_data):
        return False
    print(f"✓ Created placeholder entry in {os.path.basename(shard_path)}")
    
    if subtopic_slug:
        link_formula_to_subtopic(formula_id, subtopic_slug)
        
    scaffold_to_formula_payload(formula_id, shard_data[formula_id])
    return True

def link_formula_to_subtopic(formula_id: str, subtopic_slug: str):
    index_path = "app/config/content/search_index.json"
    if not os.path.exists(index_path):
        print("Error: search_index.json not found.")
        return False
        
    with open(index_path, 'r', encoding='utf-8') as f:
        try:
            search_index = json.load(f)
        except Exception as e:
            print(f"Error loading search index: {e}")
            return False
            
    if subtopic_slug not in search_index:
        print(f"Error: Subtopic '{subtopic_slug}' not found in search index.")
        return False
        
    shard_name = search_index[subtopic_slug].get("s")
    if not shard_name:
        print(f"Error: No shard mapped for subtopic '{subtopic_slug}'.")
        return False
        
    shard_path = os.path.join("app/config/content", shard_name)
    if not os.path.exists(shard_path):
        print(f"Error: Shard file {shard_path} does not exist.")
        return False
        
    with open(shard_path, 'r', encoding='utf-8') as f:
        try:
            shard_data = json.load(f)
        except Exception as e:
            print(f"Error loading subtopic shard {shard_path}: {e}")
            return False
            
    if subtopic_slug not in shard_data:
        print(f"Error: Subtopic '{subtopic_slug}' not found in shard {shard_name}.")
        return False
        
    subtopic = shard_data[subtopic_slug]
    if "formula_ids" not in subtopic:
        subtopic["formula_ids"] = []
        
    if formula_id not in subtopic["formula_ids"]:
        subtopic["formula_ids"].append(formula_id)
        if save_json_atomically(shard_path, shard_data):
            print(f"✓ Linked formula '{formula_id}' to subtopic '{subtopic_slug}' in {shard_name}")
            return True
    else:
        print(f"Notice: Formula '{formula_id}' is already linked to subtopic '{subtopic_slug}'.")
        return True
    return False

def formula_auto_seed(limit=5, rate_tier="free"):
    """Scans subtopic contents for unregistered formulas, uses Gemini to generate titles/IDs,
    registers placeholders in shards, auto-seeds them, compiles them to SVGs, and syncs to database.
    """
    import glob
    import re
    import html
    import hashlib
    import time
    import keyring
    import os
    import tempfile
    import socket
    
    # 1. Configure the Gemini client
    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import APIError
    except ImportError:
        print("Error: The 'google-genai' package is not installed.")
        return

    api_key = os.environ.get("GEMINI_API_KEY") or keyring.get_password("physics_lab", "gemini_api_key")
    gcp_project = os.environ.get("GCP_PROJECT_ID")
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    is_vertex = bool(gcp_project and credentials_path)

    if is_vertex:
        print(f"Initializing Vertex AI client for project: {gcp_project}", flush=True)
        client = genai.Client(
            vertexai=True,
            project=gcp_project,
            location="us-central1",
            http_options=types.HttpOptions(timeout=30_000)
        )
        MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-flash-lite")
    else:
        if not api_key:
            print("Error: No GEMINI_API_KEY found in environment or keyring.")
            return
        if api_key.startswith("AQ.") or api_key.startswith("ya29."):
            from google.oauth2.credentials import Credentials
            client = genai.Client(credentials=Credentials(token=api_key), http_options=types.HttpOptions(timeout=30_000))
        else:
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30_000))
        MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-flash-latest")
    print(f"Using Model: {MODEL_NAME}", flush=True)

    # 2. Audit to find unregistered formulas
    print("🛡️ Scanning subtopics for unregistered equations...")
    registered_latex = set()
    shards_dir = "app/config/content/formulas"
    for shard_path in glob.glob(os.path.join(shards_dir, "shard_*.json")):
        with open(shard_path, 'r', encoding='utf-8') as f:
            try:
                shard_data = json.load(f)
                for f_id, formula in shard_data.items():
                    eqn = formula.get("equation", "")
                    if eqn:
                        if "data-tex=" in eqn:
                            match = re.search(r'data-tex="([^"]+)"', eqn)
                            if match:
                                latex = html.unescape(match.group(1))
                                registered_latex.add(clean_latex(latex))
                        else:
                            registered_latex.add(clean_latex(eqn))
            except Exception:
                pass

    subtopics_dir = "app/config/content/"
    unregistered = {}
    relation_operators = ["=", "\\propto", "\\approx", "\\le", "\\ge", "<", ">", "\\to", "\\implies"]

    for filepath in glob.glob(os.path.join(subtopics_dir, "*.json")):
        basename = os.path.basename(filepath)
        if basename in ["categories.json", "search_index.json", "constants.json", "entities.json", "particles.json", "compiled_trie_regex.json", "formula_aliases.json"]:
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for subtopic_slug, subtopic in data.items():
                    if not isinstance(subtopic, dict):
                        continue
                    content = subtopic.get("content", "")
                    matches = re.findall(r'data-tex="([^"]+)"', content)
                    for raw_latex in matches:
                        latex = html.unescape(raw_latex)
                        if not any(op in latex for op in relation_operators):
                            continue
                        norm = clean_latex(latex)
                        if norm and norm not in registered_latex:
                            if latex not in unregistered:
                                unregistered[latex] = []
                            if subtopic_slug not in unregistered[latex]:
                                unregistered[latex].append(subtopic_slug)
            except Exception:
                pass

    if not unregistered:
        print("✓ All equations in subtopic articles are already registered in the database!")
        return

    # Sort unregistered formulas by reference frequency
    sorted_unregistered = sorted(unregistered.items(), key=lambda x: len(x[1]), reverse=True)
    target_unregistered = sorted_unregistered[:limit]

    print(f"Found {len(unregistered)} unregistered formulas. Target limit is {limit}.")
    print("Top candidates selected for registration and seeding:")
    for latex, subtopics in target_unregistered:
        print(f"  * {latex} (used in {len(subtopics)} subtopic(s))")

    # 3. Generate Naming and IDs via Gemini API
    print("\n🤖 Calling Gemini API to structure titles and slugs...")
    prompt = (
        "You are an expert physics editor. Given the following LaTeX equations, "
        "provide the standard physical title and a clean lowercase alphanumeric ID/slug using hyphens for each. "
        "Make sure the ID is descriptive (e.g. 'fundamental-thermodynamic-relation' for 'dU = T dS - P dV + ...').\n\n"
    )
    for i, (latex, _) in enumerate(target_unregistered):
        prompt += f"{i+1}. LaTeX: {latex}\n"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FormulaNamingList
            )
        )
        namings = json.loads(response.text).get("namings", [])
    except Exception as e:
        print(f"API Error generating names: {e}")
        return

    # 4. Create formula placeholders and links in shards
    created_formulas = []
    for naming in namings:
        latex = naming.get("latex", "")
        title = naming.get("title", "")
        fid = naming.get("id", "").strip().lower()
        
        # Find original subtopics references
        orig_latex = None
        for k, v in target_unregistered:
            if clean_latex(k) == clean_latex(latex):
                orig_latex = k
                break
        if not orig_latex:
            continue
            
        subtopics = unregistered[orig_latex]
        first_subtopic = subtopics[0]
        
        print(f"\nCreating placeholder formula '{fid}' (Title: '{title}'):")
        if create_formula_entry(fid, title, orig_latex, first_subtopic):
            for subtopic_slug in subtopics[1:]:
                link_formula_to_subtopic(fid, subtopic_slug)
            created_formulas.append(fid)

    if not created_formulas:
        print("\nNo formulas were created.")
        return

    # 5. Run standard GQS seed to enrich the newly created placeholders
    print("\n🌱 Seeding contents & explanations for the new formulas...")
    seed(rate_tier)

    # 6. Pre-render MathJax SVGs via orchestrator compiler
    print("\n🎨 Pre-rendering formulas into SVGs...")
    try:
        subprocess.run(["python3", "scratch/compile_formulas.py"])
        print("✓ Formulas compiled to SVG.")
    except Exception as e:
        print(f"  ⚠️ Compilation failed: {e}")

    # 7. Run database CLI synchronization to push to MariaDB
    print("\n🔄 Synchronizing database tables...")
    try:
        subprocess.run(["php", "cli_sync.php"])
        print("✓ Database table sync completed.")
    except Exception as e:
        print(f"  ⚠️ Database sync failed: {e}")

    print("\n🚀 SUCCESS: Auto-registration, seeding, rendering, and database sync complete!")

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
    elif cmd == "formula-create":
        if len(sys.argv) < 5:
            print("Error: Missing arguments for formula-create.")
            print("Usage: .venv/bin/python3 gqs.py formula-create <formula-id> <title> <latex-equation> [subtopic-slug]")
            sys.exit(1)
        fid = sys.argv[2]
        title = sys.argv[3]
        latex = sys.argv[4]
        slug = sys.argv[5] if len(sys.argv) > 5 else None
        create_formula_entry(fid, title, latex, slug)
    elif cmd == "formula-link":
        if len(sys.argv) < 4:
            print("Error: Missing arguments for formula-link.")
            print("Usage: .venv/bin/python3 gqs.py formula-link <formula-id> <subtopic-slug>")
            sys.exit(1)
        fid = sys.argv[2]
        slug = sys.argv[3]
        link_formula_to_subtopic(fid, slug)
    elif cmd == "formula-auto-seed":
        limit = 5
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                pass
        rate_tier = sys.argv[3] if len(sys.argv) > 3 else "free"
        formula_auto_seed(limit, rate_tier)
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
        print("  formula-create    Create a brand new formula and scaffold it for seeding")
        print("  formula-link      Link an existing formula to a subtopic")
        print("  formula-auto-seed Auto-register and AI-seed N missing equations from subtopic articles")
        sys.exit(1)

if __name__ == "__main__":
    main()
