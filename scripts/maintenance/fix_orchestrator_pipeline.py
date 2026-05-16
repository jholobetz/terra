import re
from orchestrator import PhysicsOrchestrator

def patch_orchestrator():
    file_path = "orchestrator.py"
    with open(file_path, "r") as f:
        content = f.read()

    # 1. Patch get_svg_snippet to preserve existing SVGs
    old_svg_snippet = """    def get_svg_snippet(self, content, color='#FFD700'):
        \"\"\"Generates a snippet where math is replaced by static SVG paths.\"\"\"
        if not content: return \"\"\"
    
    new_svg_snippet = """    def get_svg_snippet(self, content, color='#FFD700'):
        \"\"\"Generates a snippet where math is replaced by static SVG paths.\"\"\"
        if not content: return \"\"
        
        # 1. Mask existing SVGs to protect them from tag stripping
        svg_blocks = []
        def mask_existing_svg(match):
            placeholder = f"___EXISTING_SVG_{len(svg_blocks)}___"
            svg_blocks.append(match.group(0))
            return placeholder
        
        content = re.sub(r'<svg.*?</svg>', mask_existing_svg, content, flags=re.DOTALL)
"""
    # Using a more surgical replacement for the start of the function
    content = content.replace("    def get_svg_snippet(self, content, color='#FFD700'):\n        \"\"\"Generates a snippet where math is replaced by static SVG paths.\"\"\"\n        if not content: return \"\"", new_svg_snippet)

    # Update placeholders in get_svg_snippet
    content = content.replace("        final_snippet = re.sub(r'___MATH_BLOCK_(\d+)___', restore_and_convert, snippet_masked)", 
                              "        final_snippet = re.sub(r'___MATH_BLOCK_(\d+)___', restore_and_convert, snippet_masked)\n        \n        # Restore existing SVGs\n        for i, svg in enumerate(svg_blocks):\n            final_snippet = final_snippet.replace(f'___EXISTING_SVG_{i}___', svg)")

    # 2. Patch get_hero_math to support existing SVGs
    old_hero_math = """    def get_hero_math(self, content, color='#FFD700'):
        \"\"\"Extracts the first technical formula to use as a stylized card badge.\"\"\"
        if not content: return \"\"
        # Find the first math block (prioritize display math)
        display_match = re.search(r'\\\\{1,2}\[(.*?)\\\\{1,2}\]', content, flags=re.DOTALL)
        if display_match:
            return self.convert_to_svg(display_match.group(1).strip(), True, color=color)"""

    new_hero_math = """    def get_hero_math(self, content, color='#FFD700'):
        \"\"\"Extracts the first technical formula to use as a stylized card badge.\"\"\"
        if not content: return \"\"
        
        # 0. Check for already rendered SVGs (Platinum fallback)
        # Prioritize display-styled SVGs
        svg_display_match = re.search(r'<div class=\"math-display\".*?>(<svg.*?</svg>)</div>', content, flags=re.DOTALL)
        if svg_display_match:
            return svg_display_match.group(1)
        
        # Then any SVG
        svg_match = re.search(r'<svg.*?</svg>', content, flags=re.DOTALL)
        if svg_match:
            return svg_match.group(0)

        # Find the first math block (prioritize display math)
        display_match = re.search(r'\\+\[(.*?)\\+\]', content, flags=re.DOTALL)
        if display_match:
            return self.convert_to_svg(display_match.group(1).strip(), True, color=color)"""

    # Note: escape backslashes for regex matching in python script
    content = re.sub(r'def get_hero_math\(self, content, color=\'#FFD700\'\):\n\s+\"\"\"Extracts the first technical formula to use as a stylized card badge.\"\"\"\n\s+if not content: return \"\"\n\s+# Find the first math block \(prioritize display math\)\n\s+display_match = re\.search\(r\'\\\\{1,2}\\\[\(.*?\)\\\\{1,2}\\\]\', content, flags=re\.DOTALL\)\n\s+if display_match:\n\s+return self\.convert_to_svg\(display_match\.group\(1\)\.strip\(\), True, color=color\)', 
                    new_hero_math, content)

    # 3. Swap order in save()
    # Find the block where render_content_to_svg is called
    content = content.replace("""                # Auto-render main content if Platinum
                if subtopic.get("standard") == "platinum":
                    self.render_content_to_svg(slug)
                
                content = subtopic.get("content", "")""", 
                """                content = subtopic.get("content", "")
                
                # IMPORTANT: Generate snippets BEFORE pre-rendering content to SVGs
                # This ensures snippet generators have raw LaTeX to work with if possible,
                # though our patched generators now handle both.
                subtopic["snippet"] = self.get_safe_snippet(content)
                subtopic["snippet_svg"] = self.get_svg_snippet(content, color=color)
                subtopic["hero_math"] = self.get_hero_math(content, color=color)

                # Auto-render main content if Platinum
                if subtopic.get("standard") == "platinum":
                    self.render_content_to_svg(slug)""")

    # Remove redundant Phase 2 in save()
    content = content.replace("""            print(f"Phase 2: Generating snippets for {len(target_slugs)} subtopics...")
            for slug in target_slugs:
                if slug not in self.data["subtopics"]: continue
                subtopic = self.data["subtopics"][slug]
                content = subtopic.get("content", "")
                color = "#FFD700" # Math Standard
                subtopic["snippet"] = self.get_safe_snippet(content)
                subtopic["snippet_svg"] = self.get_svg_snippet(content, color=color)
                subtopic["hero_math"] = self.get_hero_math(content, color=color)""", "")

    with open(file_path, "w") as f:
        f.write(content)
    print("Orchestrator pipeline patched.")

if __name__ == "__main__":
    patch_orchestrator()
