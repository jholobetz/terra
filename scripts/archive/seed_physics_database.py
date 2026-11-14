#!/usr/bin/env python3
"""
🔬 PHYSICS LAB: Database Seeder
Enriches empty/placeholder formula entries across the 256 JSON shards using the modern google-genai SDK.
"""

import os
import sys
import re
import json
import time
import glob
import html
import tempfile
from typing import Dict
from pydantic import BaseModel, Field
import keyring
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Define Pydantic Schema for Structured Output
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

def main():
    rate_tier = sys.argv[1].lower() if len(sys.argv) > 1 else "free"
    
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
        print(f"Checking shard: {os.path.basename(filepath)}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                shard_data = json.load(f)
            except Exception as e:
                print(f"Error loading {os.path.basename(filepath)}: {e}")
                return
        
        updated = False
        
        for formula_id, formula in shard_data.items():
            if formula.get("interpretation") in ["Analysis pending.", "Analysis pending"]:
                title = formula.get("title", "Unknown Formula")
                svg_eq = formula.get("equation", "")
                latex_src = extract_latex_from_svg(svg_eq)
                
                if not latex_src:
                    print(f"  Skipping '{title}' (Unable to parse LaTeX from SVG)")
                    continue
                    
                print(f"  -> Seeding missing definition for: '{title}'...")
                
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
                            print(f"    Temporary error {e.code} (attempt {attempt + 1}/{max_retries}). Sleeping for {backoff_delay} seconds...")
                            time.sleep(backoff_delay)
                            backoff_delay *= 2
                        else:
                            print(f"    API Error generating content for '{title}': {e}")
                            break
                    except Exception as e:
                        print(f"    General Error generating content for '{title}': {e}")
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
                print(f"  Saved changes to {os.path.basename(filepath)}")
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"  Error saving changes to {os.path.basename(filepath)}: {e}")

    shard_files = glob.glob(os.path.join(SHARDS_DIR, "shard_*.json"))
    shard_files.sort()
    
    if not shard_files:
        print(f"No formula JSON shards found in {SHARDS_DIR}")
        return
        
    print(f"Found {len(shard_files)} shards. Commencing GQS Database Seeding...")
    for filepath in shard_files:
        process_shard(filepath)
    print("Database seeding completed.")

if __name__ == "__main__":
    main()
