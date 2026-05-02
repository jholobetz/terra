import re
import sys

path = 'orchestrator.py'
with open(path, 'r') as f:
    content = f.read()

new_method = """    def apply_auto_links(self, slug, dry_run=False):
        if slug not in self.data["subtopics"]:
            return None
        
        topic = self.data["subtopics"][slug]
        content = topic["content"]
        original_content = content
        
        # 1. Entity Linking (Historical Figures/Facilities)
        content = self._apply_entity_links(content)

        # 2. Mask MathJax AND existing links to prevent corruption
        masked_content, placeholders = self.mask_mathjax(content)
        
        # Mask <a> tags
        link_placeholders = {}
        link_count = 0
        def link_masker(match):
            nonlocal link_count
            ph = f"##LINK_PH_{link_count}##"
            link_placeholders[ph] = match.group(0)
            link_count += 1
            return ph
        
        masked_content = re.sub(r'<a\s+[^>]*>.*?</a>', link_masker, masked_content, flags=re.DOTALL)
        
        # Performance optimization: get titles for current slug once
        current_titles = [t for t, s in self.registry.items() if s == slug]

        for title in self.sorted_titles:
            target_slug = self.registry[title]
            if target_slug == slug or title in current_titles:
                continue
            
            link_html = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link"><strong>{title}</strong></a>'
            bold_tag = f"<strong>{title}</strong>"
            
            if bold_tag in masked_content:
                masked_content = masked_content.replace(bold_tag, link_html)
            else:
                # For plain text, ensure we are not inside a tag attribute
                plain_pattern = re.compile(rf'(?<![=">/])\\\\b{re.escape(title)}\\\\b(?![^<]*>)')
                masked_content = plain_pattern.sub(lambda m: link_html, masked_content)
        
        # Unmask links
        for ph, original in link_placeholders.items():
            masked_content = masked_content.replace(ph, original)
            
        final_content = self.unmask_mathjax(masked_content, placeholders)
        final_content = self._sanitize_mathjax(final_content)
        
        if not dry_run:
            topic["content"] = final_content
            
        return final_content if final_content != original_content else None"""

# Replace the whole method
pattern = re.compile(r'    def apply_auto_links\(self, slug, dry_run=False\):.*?return final_content if final_content != original_content else None', re.DOTALL)
content = pattern.sub(new_method, content)

with open(path, 'w') as f:
    f.write(content)
