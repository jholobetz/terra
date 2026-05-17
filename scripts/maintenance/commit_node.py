import sys
import json
import os
import shutil

def commit_node(slug, html_file):
    # 1. Read HTML
    with open(html_file, 'r') as f:
        html_content = f.read()

    # 2. Get Shard
    from orchestrator import PhysicsOrchestrator
    orch = PhysicsOrchestrator()
    if slug not in orch.slug_to_shard:
        print(f"Error: Slug {slug} not found in any shard.")
        sys.exit(1)
        
    shard_name = orch.slug_to_shard[slug]
    shard_path = os.path.join("app/config/content", shard_name)
    
    # Backup shard
    shutil.copy(shard_path, shard_path + ".bak")

    # Update JSON
    with open(shard_path, 'r') as f:
        shard_data = json.load(f)
        
    # Generate snippet from first ~25 words of text (stripping HTML)
    import re
    text_only = re.sub(r'<[^>]+>', '', html_content)
    snippet = " ".join(text_only.split()[:30]) + "..."
    
    shard_data[slug]['content'] = html_content
    shard_data[slug]['standard'] = 'platinum'
    shard_data[slug]['snippet'] = snippet
    
    with open(shard_path, 'w') as f:
        json.dump(shard_data, f, indent=4)
        
    try:
        # 3. Auto Linker
        from auto_linker import run_auto_linker
        run_auto_linker([shard_path], 'app/config/content/search_index.json')
        
        # 4. SVG Rendering
        orch = PhysicsOrchestrator() # Re-init to pick up linked content
        orch.render_content_to_svg(slug)
        orch.save(force_full=True, unlock_protected=True)
        
        # 4b. Rebuild Parent Hub Caches
        parents = orch.data["subtopics"].get(slug, {}).get("parents", [])
        for p in parents:
            if p in orch.data["topics"]:
                print(f"Rebuilding hub cache for: {p}")
                try:
                    orch.build(slug=p)
                except Exception as build_err:
                    print(f"Warning: Could not hit local server to build {p}. Deleting cache file instead.")
                
                cache_file = f"public/cache/topic/{p}.html"
                if os.path.exists(cache_file):
                    os.remove(cache_file)

        # 4c. Targeted MariaDB Sync
        print(f"Injecting {slug} into MariaDB...")
        os.system(f"php scripts/maintenance/sync_node.php {slug}")
        
        # 5. Integrity Shield
        from integrity_shield import IntegrityShield
        shield = IntegrityShield()
        
        # We want to check if this specific slug passes. We'll run full shield and check errors.
        success = shield.run()
        if not success:
            # Check if errors are related to this slug
            slug_errors = [e for e in shield.errors if f"[{slug}]" in e]
            if slug_errors:
                print(f"Integrity Shield failed for {slug}:")
                for e in slug_errors:
                    print(e)
                raise Exception("Integrity Shield Validation Failed")
            else:
                print("Integrity Shield failed for other reasons, but ignoring for now or you can handle it.")
                
        # 6. Advance Sprint
        with open('sprint.json', 'r') as f:
            sprint = json.load(f)
            
        # mark current as platinum
        for item in sprint['queue']:
            if item['slug'] == slug:
                item['status'] = 'platinum'
                
        # find next
        next_slug = None
        for item in sprint['queue']:
            if item['status'] == 'pending':
                next_slug = item['slug']
                break
                
        if next_slug:
            sprint['next_target'] = next_slug
        else:
            sprint['next_target'] = 'Pillar Complete'
            
        with open('sprint.json', 'w') as f:
            json.dump(sprint, f, indent=4)
            
        print(f"Successfully committed {slug}. Next target: {sprint['next_target']}")
        
    except Exception as e:
        print(f"Failed: {e}")
        # Revert
        shutil.copy(shard_path + ".bak", shard_path)
        print("Reverted shard to backup.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 commit_node.py <slug> <html_file>")
        sys.exit(1)
    commit_node(sys.argv[1], sys.argv[2])
