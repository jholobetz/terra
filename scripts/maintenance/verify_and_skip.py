import sys
import json
import os
import re
from datetime import datetime

ACTIVE_SPRINT_PATH = 'subfiles/active_expansion_sprint.json'

def verify_and_skip(slug):
    print(f"--- PRE-FLIGHT VERIFICATION: {slug} ---")
    
    # 1. Get Shard and Data
    from orchestrator import PhysicsOrchestrator
    orch = PhysicsOrchestrator()
    if slug not in orch.slug_to_shard:
        print(f"ERROR: Slug {slug} not found in search index.")
        sys.exit(1)
        
    shard_name = orch.slug_to_shard[slug]
    shard_path = os.path.join("app/config/content", shard_name)
    
    with open(shard_path, 'r') as f:
        shard_data = json.load(f)
    
    node = shard_data.get(slug)
    if not node:
        print(f"ERROR: Node {slug} not found in {shard_path}.")
        sys.exit(1)
        
    content = node.get('content', '')
    standard = node.get('standard', '')
    title = node.get('title', '')
    
    # 2. Check Standard
    if standard != 'platinum':
        print(f"REJECTED: Standard is '{standard}', not 'platinum'.")
        sys.exit(1)
        
    # 3. Robust Word Count
    clean_content = re.sub(r'<svg.*?>.*?</svg>', '', content, flags=re.DOTALL)
    text_only = re.sub(r'<[^>]+>', '', clean_content)
    words = text_only.split()
    word_count = len(words)
    
    if word_count < 650:
        print(f"REJECTED: Word count {word_count} is below 650 threshold.")
        sys.exit(1)
        
    # 4. Mandatory Checks
    
    # A. The "In Media Res" Lead
    first_15 = " ".join(words[:15]).lower()
    clean_title = title.lower().replace("the ", "").strip()
    if clean_title in first_15:
         print(f"REJECTED: 'In Media Res' lead violation. Title snippet '{clean_title}' found in first 15 words.")
         sys.exit(1)
    
    # B. Zero-Artifact Prose (Expanded to detect headers)
    artifacts = ['<ul>', '<li>', '<ol>', '---', '***', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>']
    if any(tag in content.lower() for tag in artifacts):
        print(f"REJECTED: Structural artifacts (lists/headers/fragmentation) detected.")
        sys.exit(1)
        
    print(f"✓ VERIFIED: {slug} is already OPS-compliant (Word count: {word_count}).")

    # 5. Advance Active Sprint (The "Skip" Logic)
    if os.path.exists(ACTIVE_SPRINT_PATH):
        with open(ACTIVE_SPRINT_PATH, 'r') as f:
            sprint = json.load(f)

        found = False
        for item in sprint.get('queue', []):
            if item.get('slug') == slug:
                item['status'] = 'completed'
                found = True
                break

        if not found:
            sprint.setdefault('ad_hoc_graduations', []).append({
                'slug': slug,
                'graduated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'verify_and_skip'
            })
            print(f"Warning: {slug} not in active sprint queue. Recorded as ad-hoc graduation.")

        next_slug = next(
            (item['slug'] for item in sprint.get('queue', []) if item.get('status') == 'pending'),
            None
        )
        sprint['active_target'] = next_slug
        sprint['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        with open(ACTIVE_SPRINT_PATH, 'w') as f:
            json.dump(sprint, f, indent=4)
            f.write('\n')

        target_msg = next_slug if next_slug else 'Sprint Complete'
        print(f"✓ SPRINT ADVANCED: Next target is {target_msg}")

    print(f"ACTION: SKIPPING refactor for {slug}.")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 verify_and_skip.py <slug>")
        sys.exit(1)
    verify_and_skip(sys.argv[1])
