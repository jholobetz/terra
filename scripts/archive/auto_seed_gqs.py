#!/usr/bin/env python3
"""
🔬 PHYSICS LAB: Keyless Auto-Seeder
Programmatically leases a local Antigravity Agent to enrich formulas in batches of 10.
"""

import asyncio
import os
import sys
import json
import re

# Add project root to sys.path to import gqs
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import gqs
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

PAYLOAD_PATH = os.path.join(PROJECT_ROOT, "subfiles/formula_payload.json")

async def enrich_formula(agent, f_id, data):
    title = data.get("title", "Unknown Formula")
    latex = data.get("latex", "")
    
    print(f"  -> Drafting metadata for: '{title}' ({f_id})...", flush=True)
    
    prompt = f"""
You are an expert physics professor and digital encyclopedia curator.
Analyze this formula:
Title: {title}
LaTeX Equation: {latex}

Generate the detailed physics explanation and semantic variables dictionary.
Return ONLY a raw JSON block containing these exact keys (do not include markdown formatting or ```json wrapper):
{{
  "conceptual_definition": "A high-level conceptual explanation of what this physics formula represents.",
  "intuitive_summary": "A concise, single-sentence summary of the physical intuition behind the equation.",
  "interpretation": "A paragraph explaining the role of variables in the equation and their physical relationships.",
  "symmetry_origin": "The coordinate invariance, conservation law, or physical derivation origin.",
  "limits_and_boundary": "Asymptotic limits when variables approach zero or infinity.",
  "semantic_variables": {{
    "symbol": {{
      "name": "The physical name of the variable",
      "type": "variable" or "constant",
      "unit": "The standard SI units",
      "description": "Detailed explanation of what this variable represents in this context"
    }}
  }}
}}

Constraints:
1. Ensure all descriptions are mathematically rigorous and educational.
2. Format variables in text with LaTeX inline delimiters: \\( variable \\).
3. Ensure SI units are standard (e.g. kg, m/s^2, J).
4. Do not include any text, notes, or markdown wrappers outside of the raw JSON object.
"""
    try:
        response = await agent.chat(prompt)
        text_content = ""
        async for token in response:
            text_content += token
            
        # Clean text in case agent wraps it in markdown codeblocks
        clean_text = text_content.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        result = json.loads(clean_text)
        return result
    except Exception as e:
        print(f"  ⚠️ Error generating content for '{title}': {e}", flush=True)
        return None

async def main():
    print("=" * 80)
    print("🪐 PHYSICS LAB: KEYLESS AUTO-SEEDER STARTING".center(80))
    print("=" * 80)
    
    config = LocalAgentConfig(
        system_instructions="You are a precise JSON drafting agent. Output only raw JSON.",
        capabilities=CapabilitiesConfig()
    )
    
    # Initialize the programmatically leased local agent
    print("Leasing local Antigravity Agent from the platform...", flush=True)
    async with Agent(config) as agent:
        print("✓ Agent leased successfully. Commencing batch loop.\n", flush=True)
        
        batch_num = 1
        while True:
            # 1. Check current status
            print(f"\n--- Batch #{batch_num} ---", flush=True)
            
            # Clear payload and template the next 10 items
            if os.path.exists(PAYLOAD_PATH):
                with open(PAYLOAD_PATH, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                    
            gqs.generate_formula_template(10)
            
            if not os.path.exists(PAYLOAD_PATH):
                print("No payload generated. Seeding completed!")
                break
                
            with open(PAYLOAD_PATH, 'r', encoding='utf-8') as f:
                payload = json.load(f)
                
            if not payload:
                print("🎉 Seeding completed! No more pending formulas in the catalog.")
                break
                
            print(f"Loaded {len(payload)} formulas to process in this batch.", flush=True)
            
            updated_count = 0
            for f_id, data in list(payload.items()):
                result = await enrich_formula(agent, f_id, data)
                if result:
                    # Update local draft dict
                    payload[f_id]["conceptual_definition"] = result.get("conceptual_definition", "")
                    payload[f_id]["intuitive_summary"] = result.get("intuitive_summary", "")
                    payload[f_id]["interpretation"] = result.get("interpretation", "")
                    payload[f_id]["symmetry_origin"] = result.get("symmetry_origin", "")
                    payload[f_id]["limits_and_boundary"] = result.get("limits_and_boundary", "")
                    payload[f_id]["semantic_variables"] = result.get("semantic_variables", {})
                    updated_count += 1
                
                # Write progressively to payload path
                with open(PAYLOAD_PATH, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=4, ensure_ascii=False)
                    
            if updated_count > 0:
                print("\nGraduating drafted definitions...", flush=True)
                gqs.ingest_formulas()
                print("Batch graduation complete.", flush=True)
            else:
                print("⚠️ No formulas were successfully updated in this batch. Aborting loop to prevent infinite retry.", flush=True)
                break
                
            batch_num += 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
