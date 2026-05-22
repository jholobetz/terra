import json
import re
import os
import subprocess
import shutil
import hashlib
import sys
from multiprocessing import Pool, cpu_count

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class TrieRegexCompiler:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def _build_regex(self, node):
        if not node.children:
            return ""
        
        alternatives = []
        for char, child_node in sorted(node.children.items()):
            suffix = self._build_regex(child_node)
            escaped_char = re.escape(char)
            if suffix:
                alternatives.append(escaped_char + suffix)
            else:
                alternatives.append(escaped_char)
                
        if len(alternatives) == 1:
            result = alternatives[0]
        else:
            result = "(?:" + "|".join(alternatives) + ")"
            
        if node.is_end:
            result += "?"
        return result

    def compile(self, words):
        valid_words = [w for w in words if isinstance(w, str) and w.strip()]
        if not valid_words:
            return r"\b\B"
        for word in valid_words:
            self.insert(word)
        return r"\b" + self._build_regex(self.root) + r"\b"

class PhysicsOrchestrator:
    PROTECTED_TOPICS = {
        "classical-mechanics", "electromagnetism", "relativity", "quantum-physics",
        "standard-model", "astrophysics", "theoretical-physics", "thermodynamics-statistical-mechanics",
        "condensed-matter", "fluids-nonlinear", "mathematical-methods", "philosophy-of-physics"
    }

    # Terms that are too common to auto-link in plain text (must be bolded to link)
    AMBIGUOUS_TERMS = {
        "Mass", "Force", "Spin", "Field", "Charge", "Energy", "Time", "Space", 
        "Work", "State", "Scale", "Phase", "Flow", "Bits", "Vacuum", "Current", 
        "Wave", "Source", "Logic", "Point", "Group"
    }

    # Terms that require technical 'anchors' nearby to auto-link in plain text
    TERM_ANCHORS = {
        "Mass": ["rest", "invariant", "relativistic", "energy", "gravity", "defect", "higgs"],
        "Field": ["gauge", "force", "electromagnetic", "scalar", "tensor", "interaction", "gradient"],
        "Spin": ["quantum", "pauli", "boson", "fermion", "angular momentum", "half-integer"],
        "Entropy": ["thermodynamics", "boltzmann", "statistical", "disorder", "information", "second law"],
        "Action": ["lagrangian", "hamilton", "stationary", "integral", "variational", "principle"],
        "Phase": ["transition", "space", "diagram", "berry", "geometric", "state"],
        "Current": ["density", "charge", "flow", "ampere", "magnetic", "displacement"],
        "Wave": ["function", "equation", "packet", "interference", "diffraction", "propagation"]
    }

    def __init__(self, content_dir="app/config/content", registry_path="global_slug_registry.json"):
        self.content_dir = content_dir
        self.registry_path = registry_path
        self.svg_engine = os.path.join(os.getcwd(), "scripts/tex2svg.js")
        self.svg_cache_path = "global_svg_cache.json"
        self.build_manifest_path = "build_manifest.json"
        self.svg_cache = {}
        self.build_manifest = {}
        self.shards = {} # Subtopic shards
        self.topic_shards = {} # Main topic shards
        self.slug_to_shard = {}
        self.shard_to_slugs = {}
        self.modified_slugs = set() # Track slugs changed in current session

        # Load SVG Cache if it exists
        if os.path.exists(self.svg_cache_path):
            try:
                with open(self.svg_cache_path, "r") as f:
                    self.svg_cache = json.load(f)
                print(f"LOADED: {len(self.svg_cache)} pre-rendered SVGs from persistent cache.")
            except Exception as e:
                print(f"CACHE WARNING: Failed to load SVG cache: {str(e)}")

        # Load Build Manifest if it exists
        if os.path.exists(self.build_manifest_path):
            try:
                with open(self.build_manifest_path, "r") as f:
                    self.build_manifest = json.load(f)
                print(f"LOADED: Build manifest with {len(self.build_manifest)} hashes.")
            except Exception as e:
                print(f"MANIFEST WARNING: Failed to load build manifest: {str(e)}")

        self.data = {
            "topics": {}, # Meta registry
            "topic_contents": {}, # Loaded content for main topics
            "subtopics": {},
            "formula_registry": {},
            "constants": {},
            "entities": {}
        }

        # Load Global Slug Registry
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {}

        self._load_content()
        self._refresh_sorted_titles()

    def get_file_hash(self, filepath):
        """Calculates MD5 hash of a file."""
        if not os.path.exists(filepath): return None
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def _load_content(self):
        """Loads all JSON shards from the content directory."""
        # 1. Load Topic Meta Registry
        categories_path = os.path.join(self.content_dir, "categories.json")
        if os.path.exists(categories_path):
            with open(categories_path, "r") as f:
                self.data["topics"] = json.load(f)

        # 2. Load Shards
        for root, dirs, files in os.walk(self.content_dir):
            for file in files:
                if not file.endswith(".json"): continue

                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, self.content_dir)

                with open(path, "r") as f:
                    content = json.load(f)

                if rel_path == "formulas.json":
                    self.data["formula_registry"] = content
                elif rel_path == "constants.json":
                    self.data["constants"] = content
                elif rel_path == "entities.json":
                    self.data["entities"] = content
                elif rel_path == "categories.json":
                    pass # Already loaded
                elif rel_path == "search_index.json":
                    pass
                elif rel_path.startswith("topics/"):
                    slug = file.replace(".json", "")
                    self.topic_shards[slug] = content
                    self.data["topic_contents"][slug] = content
                else:
                    # Subtopic shard
                    self.shards[rel_path] = content
                    self.shard_to_slugs[rel_path] = []
                    for slug in content:
                        self.data["subtopics"][slug] = content[slug]
                        self.slug_to_shard[slug] = rel_path
                        self.shard_to_slugs[rel_path].append(slug)
    def _refresh_sorted_titles(self):
        # Load Pillar Profiles
        self.pillar_profiles = {}
        profile_path = os.path.join(self.content_dir, "pillar_profiles.json")
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                self.pillar_profiles = json.load(f)

        self.sorted_titles = sorted(self.registry.keys(), key=len, reverse=True)
        self.registry_lower = {k.lower(): v for k, v in self.registry.items()}
        
        # Build the single-pass Trie-compiled regex for plain text keywords
        valid_trie_titles = [t for t in self.sorted_titles if t not in self.AMBIGUOUS_TERMS]
        trie_compiler = TrieRegexCompiler()
        compiled_trie = trie_compiler.compile(valid_trie_titles)
        self.compiled_plain_regex = re.compile(rf'(?<![=">])({compiled_trie})(?![<])')

    def get_link_cloud(self, text, limit=15):
        """Scans text and returns a 'cloud' of relevant links based on the registry."""
        cloud = []
        text_lower = text.lower()
        
        # self.sorted_titles is already sorted by length (desc)
        for title in self.sorted_titles:
            if len(cloud) >= limit: break
            
            slug = self.registry[title]
            # Match word boundaries to prevent partial matches like 'c' inside 'physics'
            t_norm = re.escape(title.lower())
            if re.search(rf'\b{t_norm}\b', text_lower):
                cloud.append({"title": title, "slug": slug})
        
        return cloud

    def auto_promote_hero_math(self, slug):
        """Scans subtopic content for the most 'semantically dense' LaTeX block."""
        if slug not in self.data["subtopics"]: return
        content = self.data["subtopics"][slug].get("content", "")
        
        # Find all display math blocks
        display_math = re.findall(r'\\\[(.*?)\\\]', content, re.DOTALL)
        if not display_math:
            # Fallback to inline
            display_math = re.findall(r'\\\((.*?)\\\)', content)
        
        if not display_math: return
        
        # Heuristic: longest LaTeX block is often the primary identity
        hero = max(display_math, key=len).strip()
        self.data["subtopics"][slug]["hero_math"] = f"\\[ {hero} \\]"
        print(f"AUTO-HERO: Promoted identity for [{slug}].")

    def execute_sprint(self, sprint_data, build_hub=True):
        """Executes a batch expansion of subtopics with Partial Acceptance."""
        print(f"Starting Pillar Sprint: {len(sprint_data)} topics.")
        successful_slugs = []
        failed_slugs = {}
        
        # 1. Registration Phase (Allowing links to work)
        for slug, data in sprint_data.items():
            raw_content = data.get("content", "")
            sanitized_content = self.sanitize_content(raw_content)

            
            self.data["subtopics"][slug] = {
                "title": data.get("title", slug),
                "content": sanitized_content,
                "parents": data.get("parents", []),
                "formula_ids": data.get("formula_ids", [])
            }
            self.registry[data.get("title", slug)] = slug
            self.modified_slugs.add(slug)

        self._refresh_sorted_titles()

        # 2. First Pass Validation
        for slug in sprint_data:
            # Apply links
            self.apply_auto_links(slug)
            content = self.data["subtopics"][slug]["content"]
            
            # Validate
            if not self.validate_platinum_standard(slug, content):
                print(f"SPRINT ERROR: Validation failed for [{slug}]. Rejecting.")
                failed_slugs[slug] = getattr(self, "last_validation_errors", ["Unknown validation error"])
            else:
                successful_slugs.append(slug)

        # 3. Rollback Failed Slugs
        if failed_slugs:
            for slug in failed_slugs:
                del self.data["subtopics"][slug]
                title = sprint_data[slug].get("title", slug)
                if title in self.registry and self.registry[title] == slug:
                    del self.registry[title]
                self.modified_slugs.discard(slug)
            self._refresh_sorted_titles()
            
            # Re-apply links for successful slugs now that failed ones are removed
            for slug in successful_slugs:
                raw_content = sprint_data[slug].get("content", "")
                sanitized_content = self.sanitize_content(raw_content)
                self.data["subtopics"][slug]["content"] = sanitized_content
                self.apply_auto_links(slug)

        # 4. Finalize Successful Slugs
        for slug in successful_slugs:
            self.data["subtopics"][slug]["standard"] = "platinum"
            self.auto_promote_hero_math(slug)
            print(f"SPRINT: Ingested and Certified [{slug}].")

        # 5. Save & Build
        if successful_slugs:
            self.save(auto_commit=False, unlock_protected=True)
            for slug in successful_slugs:
                self.build(slug=slug)
            
            if build_hub:
                parent = self.data["subtopics"][successful_slugs[0]]["parents"][0]
                self.build(slug=parent)
            
            print(f"SUCCESS: Sprint complete. {len(successful_slugs)} topics deployed.")
            
        return successful_slugs, failed_slugs

    def _start_mathjax_daemon(self):
        """Starts a persistent Node.js subprocess to render MathJax equations line-by-line."""
        if hasattr(self, '_mathjax_process') and self._mathjax_process and self._mathjax_process.poll() is None:
            return
        
        try:
            self._mathjax_process = subprocess.Popen(
                ["node", self.svg_engine, "--daemon"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1 # Line-buffered
            )
            print("MathJax persistent daemon started.")
        except Exception as e:
            print(f"Failed to start MathJax persistent daemon: {e}")
            self._mathjax_process = None

    def __del__(self):
        if hasattr(self, '_mathjax_process') and self._mathjax_process:
            try:
                self._mathjax_process.stdin.close()
                self._mathjax_process.terminate()
                self._mathjax_process.wait(timeout=1)
            except Exception:
                pass

    def convert_to_svg(self, clean_latex, is_display=False, color='#FFD700'):
        """Converts a clean LaTeX string (no delimiters) to SVG using the persistent MathJax daemon or fallback."""
        cache_key = f"{clean_latex}_{is_display}_{color}"
        if cache_key in self.svg_cache:
            return self.svg_cache[cache_key]

        # Try daemon mode
        self._start_mathjax_daemon()
        if hasattr(self, '_mathjax_process') and self._mathjax_process and self._mathjax_process.poll() is None:
            try:
                payload = json.dumps({
                    "latex": clean_latex,
                    "is_display": is_display,
                    "color": color
                })
                self._mathjax_process.stdin.write(payload + "\n")
                self._mathjax_process.stdin.flush()
                
                # Read response line
                response_line = self._mathjax_process.stdout.readline().strip()
                if response_line:
                    res = json.loads(response_line)
                    if "svg" in res:
                        svg_code = res["svg"]
                        self.svg_cache[cache_key] = svg_code
                        return svg_code
                    elif "error" in res:
                        print(f"Daemon MathJax Error for [{clean_latex}]: {res['error']}")
            except Exception as e:
                print(f"Daemon communication error: {e}. Falling back to subprocess...")
                try:
                    self._mathjax_process.terminate()
                except Exception:
                    pass
                self._mathjax_process = None

        # Fallback to single-shot subprocess
        try:
            mode = "display" if is_display else "inline"
            result = subprocess.run(["node", self.svg_engine, clean_latex, mode, color], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                svg_code = result.stdout.strip()
                self.svg_cache[cache_key] = svg_code
                return svg_code
        except Exception as e:
            print(f"SVG Fallback Error for [{clean_latex}]: {str(e)}")
        
        return clean_latex

    def get_svg_snippet(self, content, color='#FFD700'):
        """Generates a snippet where math is replaced by static SVG paths."""
        if not content: return ""
        
        # 1. Mask existing SVGs to protect them from tag stripping
        svg_blocks = []
        def mask_existing_svg(match):
            placeholder = f"___EXISTING_SVG_{len(svg_blocks)}___"
            svg_blocks.append(match.group(0))
            return placeholder
        
        content = re.sub(r'<svg.*?</svg>', mask_existing_svg, content, flags=re.DOTALL)

        # 2. Protect Numbered Headers
        clean = re.sub(r'\d+\.\s+[A-Z].*', '', content)
        
        # 3. Extract math blocks (preserving LaTeX inside capturing group 1)
        math_blocks = []
        def mask_math(match):
            placeholder = f"___MATH_BLOCK_{len(math_blocks)}___"
            # match.group(1) is the clean LaTeX without delimiters
            math_blocks.append((match.group(1), match.group(0)))
            return placeholder

        # Capture content between \[ \] or \( \)
        masked = re.sub(r'\\{1,2}\[(.*?)\\{1,2}\]', mask_math, clean, flags=re.DOTALL)
        masked = re.sub(r'\\{1,2}\((.*?)\\{1,2}\)', mask_math, masked, flags=re.DOTALL)
        
        # Strip other HTML tags for sentence splitting
        text_only = re.sub(r'<.*?>', '', masked)
        sentences = re.split(r'(?<=[.!?])\s+', text_only)
        snippet_masked = " ".join(sentences[:3])
        if len(sentences) > 3 and not snippet_masked.endswith('.'):
            snippet_masked += "."

        # 4. Restore and Convert Math Blocks
        def restore_and_convert(match):
            try:
                idx = int(match.group(1))
                clean_latex, original = math_blocks[idx]
                is_display = "\\[" in original or "\\\\[" in original
                return self.convert_to_svg(clean_latex.strip(), is_display, color=color)
            except:
                return ""

        final_snippet = re.sub(r'___MATH_BLOCK_(\d+)___', restore_and_convert, snippet_masked)
        
        # Restore existing SVGs
        for i, svg in enumerate(svg_blocks):
            final_snippet = final_snippet.replace(f'___EXISTING_SVG_{i}___', svg)

        # 5. Final cleanup
        final_snippet = re.sub(r'\(\s*\)', '', final_snippet)
        return final_snippet.strip()

    def get_safe_snippet(self, content):
        """Extracts a math-free 3-sentence snippet from HTML content."""
        if not content: return ""
        # 1. Strip out MathJax inline and display formulas completely
        clean = re.sub(r'\\{1,2}\[.*?\\{1,2}\]', '', content, flags=re.DOTALL)
        clean = re.sub(r'\\{1,2}\(.*?\\{1,2}\)', '', clean, flags=re.DOTALL)
        
        # 2. Strip HTML
        clean = re.sub(r'<.*?>', '', clean)
        
        # 3. Strip Numbered Headers
        clean = re.sub(r'\d+\.\s+[A-Z].*', '', clean)
        
        # 4. Cleanup orphaned parentheses like "( )" or "()"
        clean = re.sub(r'\(\s*\)', '', clean)
        
        # 5. Collapse whitespace and fix punctuation spacing
        clean = re.sub(r'\s+([.,!?])', r'\1', clean)
        clean = " ".join(clean.split())
        
        # 6. Extract 3 sentences
        sentences = re.split(r'(?<=[.!?])\s+', clean)
        snippet = " ".join(sentences[:3])
        if len(sentences) > 3 and not snippet.endswith('.'):
            snippet += "."
            
        return snippet.strip()

    def get_hero_math(self, content, color='#FFD700'):
        """Extracts the first technical formula to use as a stylized card badge."""
        if not content: return ""

        # 0. Check for already rendered SVGs (Platinum fallback)
        # Prioritize display-styled SVGs
        svg_display_match = re.search(r'<div class="math-display".*?>(<svg.*?</svg>)</div>', content, flags=re.DOTALL)
        if svg_display_match:
            return svg_display_match.group(1)
        
        # Then any SVG
        svg_match = re.search(r'<svg.*?</svg>', content, flags=re.DOTALL)
        if svg_match:
            return svg_match.group(0)

        # Find the first math block (prioritize display math)
        display_match = re.search(r'\\{1,2}\[(.*?)\\{1,2}\]', content, flags=re.DOTALL)
        if display_match:
            return self.convert_to_svg(display_match.group(1).strip(), True, color=color)
            
        inline_match = re.search(r'\\{1,2}\((.*?)\\{1,2}\)', content, flags=re.DOTALL)
        if inline_match:
            return self.convert_to_svg(inline_match.group(1).strip(), False, color=color)
            
        return ""

    def batch_convert_to_svg(self, formula_batch):
        """Converts a batch of LaTeX formulas to SVG in a single Node.js process."""
        if not formula_batch: return {}
        
        # formula_batch: { cache_key: { "latex": "...", "is_display": bool } }
        try:
            input_json = json.dumps(formula_batch)
            result = subprocess.run(["node", self.svg_engine], input=input_json, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout:
                new_svgs = json.loads(result.stdout)
                self.svg_cache.update(new_svgs)
                return new_svgs
        except Exception as e:
            print(f"BATCH SVG Error: {str(e)}")
        return {}

    def render_content_to_svg(self, slug):
        """Replaces all LaTeX delimiters in a subtopic's content with pre-rendered SVGs."""
        if slug not in self.data["subtopics"]: return
        sub = self.data["subtopics"][slug]
        content = sub.get("content", "")
        # Platinum Standard: All math is rendered in Gold #FFD700 for high-signal visibility
        color = "#FFD700"

        # 1. Replace Display Math \[ ... \]
        def replace_display(match):
            latex = match.group(1).strip()
            svg = self.convert_to_svg(latex, is_display=True, color=color)
            return f'<div class="math-display" style="text-align: center; margin: 25px 0;">{svg}</div>'
        
        content = re.sub(r'\\+\[(.*?)\\+\]', replace_display, content, flags=re.DOTALL)

        # 2. Replace Inline Math \( ... \)
        def replace_inline(match):
            latex = match.group(1).strip()
            return self.convert_to_svg(latex, is_display=False, color=color)
        
        content = re.sub(r'\\+\((.*?)\\+\)', replace_inline, content, flags=re.DOTALL)
        
        sub["content"] = content

    def render_registry_to_svg(self, color='#FFD700'):
        """Pre-renders all formulas in the registry to static SVGs."""
        print(f"Pre-rendering formula registry ({len(self.data['formula_registry'])} items) in {color}...")
        rendering_queue = {}
        
        # We need the original LaTeX to re-render. 
        # If the equation is already an SVG, we might have lost the LaTeX unless it's in a backup.
        # However, for this project, many SVGs were added by agents.
        # Let's try to extract LaTeX from the title or just skip if it's already an SVG and we can't recover.
        
        for f_id, formula in self.data["formula_registry"].items():
            eqn = formula.get("equation", "")
            if not eqn: continue
            
            # If it's already an SVG, we can't easily re-render without the source LaTeX.
            # But we can try to fix the COLOR via string replacement if it's an SVG.
            if eqn.startswith("<svg"):
                # Fix color in-place
                formula["equation"] = eqn.replace('color: #64ffda', f'color: {color}').replace('color: #64FFDA', f'color: {color}')
                continue
            
            cache_key = f"REG_{f_id}_{color}"
            rendering_queue[cache_key] = {"latex": eqn, "is_display": True, "color": color}
            
        if rendering_queue:
            print(f"  -> Batching {len(rendering_queue)} formulas...")
            new_svgs = self.batch_convert_to_svg(rendering_queue)
            
            # Update registry
            for f_id, formula in self.data["formula_registry"].items():
                cache_key = f"REG_{f_id}_{color}"
                if cache_key in self.svg_cache:
                    formula["equation"] = self.svg_cache[cache_key]
            
            print("  -> Registry pre-rendered and updated.")

    def save(self, auto_commit=True, commit_msg=None, unlock_protected=False, force_full=False):
        """Saves all modified shards and registries and optionally commits to Git."""
        # 1. Pre-render SVGs in batch for modified subtopics
        target_slugs = self.data["subtopics"].keys() if force_full else self.modified_slugs
        
        if target_slugs:
            print(f"Phase 1: Batch rendering SVGs for {len(target_slugs)} subtopics...")
            rendering_queue = {}
            for slug in target_slugs:
                if slug not in self.data["subtopics"]: continue
                subtopic = self.data["subtopics"][slug]
                content = subtopic.get("content", "")
                color = "#FFD700" # Math Standard

                # IMPORTANT: Generate snippets BEFORE pre-rendering content to SVGs
                # This ensures snippet generators have raw LaTeX to work with if possible,
                # though our patched generators now handle both.
                subtopic["snippet"] = self.get_safe_snippet(content)
                subtopic["snippet_svg"] = self.get_svg_snippet(content, color=color)
                subtopic["hero_math"] = self.get_hero_math(content, color=color)

                # Auto-render main content if Platinum
                if subtopic.get("standard") == "platinum":
                    self.render_content_to_svg(slug)
                    # Refresh content after rendering for phase 1 batching check below
                    content = subtopic.get("content", "")

                # Find all math blocks for batching
                math_blocks = re.findall(r'\\+\[.*?\\+\]|\\+\(.*?\\+\)', content, re.DOTALL)
                for latex in math_blocks:
                    # Strip delimiters for cleaner cache and engine processing
                    clean_latex = re.sub(r'^\\{1,2}\[|^\\{1,2}\(|\\{1,2}\]$|\\{1,2}\)$', '', latex).strip()
                    is_display = "\\[" in latex or "\\\\[" in latex
                    cache_key = f"{clean_latex}_{is_display}_{color}"
                    if cache_key not in self.svg_cache:
                        rendering_queue[cache_key] = {"latex": clean_latex, "is_display": is_display, "color": color}

            if rendering_queue:
                print(f"  -> Batching {len(rendering_queue)} new formulas...")
                self.batch_convert_to_svg(rendering_queue)

        # 2. Save Registries
        # Clean topics for categories.json (metadata only)
        clean_topics = {}
        for slug, meta in self.data["topics"].items():
            clean_topics[slug] = {
                "title": meta["title"],
                "shard": meta.get("shard", f"topics/{slug}.json")
            }

        with open(os.path.join(self.content_dir, "categories.json"), "w") as f:
            json.dump(clean_topics, f, indent=4)
        with open(os.path.join(self.content_dir, "formulas.json"), "w") as f:
            json.dump(self.data["formula_registry"], f, indent=4)
        with open(os.path.join(self.content_dir, "constants.json"), "w") as f:
            json.dump(self.data["constants"], f, indent=4)
        with open(os.path.join(self.content_dir, "entities.json"), "w") as f:
            json.dump(self.data["entities"], f, indent=4)
        
        # 3. Save Topic Shards (Protected)
        for slug, content in self.topic_shards.items():
            # SYNC INTRO TO CONTENT FOR HOME PAGE COMPATIBILITY
            # If the hub has transitioned to dynamic architecture (content is empty),
            # copy the intro into content so the home page card has text to display.
            if content.get("intro") and not content.get("content"):
                content["content"] = content["intro"]

            path = os.path.join(self.content_dir, "topics", f"{slug}.json")
            if os.path.exists(path) and not unlock_protected:
                # Optional: Compare hashes to see if it actually changed
                with open(path, "r") as f:
                    old_content = f.read()
                if old_content != json.dumps(content, indent=4):
                    print(f"SAFEGUARD: Skipping save for PROTECTED topic shard [{slug}]. Use unlock_protected=True to override.")
                    continue
            
            with open(path, "w") as f:
                json.dump(content, f, indent=4)
            # Record shard hash
            self.build_manifest[f"shard_topic_{slug}"] = self.get_file_hash(path)

        # 4. Save Subtopic Shards
        # Map all subtopics to their shards
        for slug, subtopic in self.data["subtopics"].items():
            found_shard = False
            for shard_name, shard_content in self.shards.items():
                if slug in shard_content:
                    shard_content[slug] = subtopic
                    found_shard = True
                    break
            
            if not found_shard:
                # NEW SUBTOPIC - Determine best shard
                # Default to the first parent's shard or theoretical-physics.json
                target_shard = "theoretical-physics.json"
                if subtopic.get("parents"):
                    p = subtopic["parents"][0]
                    if f"{p}.json" in self.shards:
                        target_shard = f"{p}.json"
                
                if target_shard not in self.shards:
                    self.shards[target_shard] = {}
                
                self.shards[target_shard][slug] = subtopic
                print(f"NEW SUBTOPIC: Assigned [{slug}] to shard [{target_shard}]")

        for shard_name, shard_content in self.shards.items():
            path = os.path.join(self.content_dir, shard_name)
            with open(path, "w") as f:
                json.dump(shard_content, f, indent=4)
            # Record shard hash
            self.build_manifest[f"shard_{shard_name}"] = self.get_file_hash(path)

        # 4.5 Update Search Index (Mapping slugs to shards with rich stats and metadata for search)
        search_index = {}
        tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]
        
        for shard_name, shard_content in self.shards.items():
            for slug, sub in shard_content.items():
                content = sub.get("content", "")
                title = sub.get("title", "Untitled")
                
                # Calculate stats for Weighting
                words = len(re.findall(r'\w+', content))
                latex_count = len(re.findall(r'\\\(|\\\[', content))
                term_score = sum(1 for term in tech_terms if term in content.lower())
                
                # Platinum Check (Current standards: 500w, 60 density)
                density_score = (latex_count * 15) + (term_score * 5)
                is_platinum = 1 if (words >= 500 and density_score >= 60) else 0

                # Keyword Extraction
                keywords = set()
                # 1. Bolded terms
                bold_matches = re.findall(r'<strong>(.*?)</strong>', content)
                for b in bold_matches:
                    clean_b = re.sub(r'<[^>]+>', '', b).strip().lower()
                    if len(clean_b) > 2: keywords.add(clean_b)
                    
                # 2. Technical Terms
                for term in tech_terms:
                    if term in content.lower():
                        keywords.add(term)
                
                # 3. Formula IDs
                for f_id in sub.get("formula_ids", []):
                    clean_fid = re.sub(r'<[^>]+>', '', f_id).replace('-', ' ')
                    keywords.add(clean_fid)

                # 4. Clean keywords
                final_keywords = set()
                for kw in keywords:
                    clean = re.sub(r'<[^>]+>', '', kw).strip().lower()
                    if len(clean) > 2 and not clean.startswith('a href'):
                        final_keywords.add(clean)

                search_index[slug] = {
                    "t": title,
                    "p": sub.get("parents", []),
                    "s": shard_name,
                    "k": list(final_keywords),
                    "w": density_score,
                    "pl": is_platinum
                }
                
        with open(os.path.join(self.content_dir, "search_index.json"), "w") as f:
            json.dump(search_index, f, indent=4)
        print(f"SUCCESS: Search index updated with {len(search_index)} entries.")

        # 5. Save Global Registry
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=4)
            
        # 6. Save SVG Cache
        try:
            with open(self.svg_cache_path, "w") as f:
                json.dump(self.svg_cache, f, indent=4)
            print(f"SAVED: {len(self.svg_cache)} SVGs to persistent cache.")

            # 7. Save Build Manifest
            with open(self.build_manifest_path, "w") as f:
                json.dump(self.build_manifest, f, indent=4)
        except Exception as e:
            print(f"CACHE WARNING: Failed to save caches: {str(e)}")

        print(f"SUCCESS: Fully sharded save complete in {self.content_dir}")

        if auto_commit:
            self.commit_to_git(commit_msg)
            
        self.modified_slugs.clear()

    def certify_all_platinum(self):
        """Batch validates all subtopics and certifies those meeting the Platinum Standard."""
        print(f"Starting batch certification for {len(self.data['subtopics'])} subtopics...")
        certified_count = 0
        legacy_count = 0
        
        for slug, subtopic in self.data["subtopics"].items():
            content = subtopic.get("content", "")
            if self.validate_platinum_standard(slug, content):
                subtopic["standard"] = "platinum"
                certified_count += 1
            else:
                subtopic["standard"] = "legacy"
                legacy_count += 1
                
        print(f"Certification complete: {certified_count} Platinum, {legacy_count} Legacy.")
        self.save(auto_commit=False)
        return certified_count

    def commit_to_git(self, message=None):
        """Automates the git commit for content changes."""
        if not message:
            message = "Great Expansion: Content Update " + subprocess.check_output(["date", "+%Y-%m-%d %H:%M"]).decode().strip()
        
        try:
            print(f"Committing to Git: {message}...")
            # Stage only content and registry
            subprocess.run(["git", "add", "app/config/content/"], check=True)
            subprocess.run(["git", "add", "global_slug_registry.json"], check=True)
            # Commit
            subprocess.run(["git", "commit", "-m", message], capture_output=True)
            print("✓ Git commit successful.")
        except Exception as e:
            print(f"WARNING: Git commit failed: {str(e)}")

    def mask_mathjax(self, content):
        placeholders = []
        pattern = re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\])', re.DOTALL)
        def replace(match):
            idx = len(placeholders)
            placeholders.append(match.group(0))
            return f"##MJ_PROTECTED_{idx}##"
        return pattern.sub(replace, content), placeholders

    def unmask_mathjax(self, content, placeholders):
        for i, original in enumerate(placeholders):
            content = content.replace(f"##MJ_PROTECTED_{i}##", original)
        return content

    def apply_auto_links(self, slug, dry_run=False):
        if slug in self.data["subtopics"]:
            topic = self.data["subtopics"][slug]
        elif slug in self.data["topic_contents"]:
            topic = self.data["topic_contents"][slug]
        else:
            return None

        content = topic["content"]
        original_content = content
        parents = topic.get("parents", [])

        # 1. Entity Linking (Historical Figures/Facilities)
        content = self._apply_entity_links(content, current_slug=slug)

        masked_content, placeholders = self.mask_mathjax(content)
        # Performance optimization: get titles for current slug once
        current_titles = [t for t, s in self.registry.items() if s == slug]
        linked_in_node = set()
        # Pre-populate already linked slugs inside masked_content to satisfy the Single Link Rule
        existing_links = re.findall(r'href=[\\"]+/physics/(?:subtopic|topic)/([^\\"/#?]+)[\\"]+', masked_content)
        for target in existing_links:
            linked_in_node.add(target)

        # Action 1: If title is BOLDED, always link it (High Intent)
        strong_pattern = re.compile(r'<strong>(.*?)</strong>')
        
        def replace_strong(match):
            inner_text = match.group(1).strip()
            # Case-insensitive alias lookup to resolve target slug
            target_slug = self.registry_lower.get(inner_text.lower())
            if not target_slug:
                return match.group(0)
                
            # Safeguard 1: Don't link a topic to itself or its alternative titles
            if target_slug == slug or inner_text in current_titles:
                return match.group(0)
                
            # Safeguard 2: Don't link to a main parent module if we are already in its shard
            if target_slug in parents:
                return match.group(0)
                
            # Ensure it's not already linked in this node
            if target_slug in linked_in_node:
                return match.group(0)
                
            # Link formatting
            if target_slug in self.data["topic_contents"]:
                url = f"/physics/topic/{target_slug}"
                link_class = "topic-link"
            else:
                url = f"/physics/subtopic/{target_slug}"
                link_class = "subtopic-link"
                
            link_html = f'<a href="{url}" class="{link_class}"><strong>{inner_text}</strong></a>'
            linked_in_node.add(target_slug)
            return link_html
            
        masked_content = strong_pattern.sub(replace_strong, masked_content)

        # Action 2: If title is PLAIN TEXT, link only if it passes contextual safeguards (Single-Pass O(N) Scan)
        def is_inside_link(pos):
            pre = masked_content[:pos]
            last_a_open = pre.rfind('<a')
            last_a_close = pre.rfind('</a>')
            return last_a_open > last_a_close

        def replace_plain(match):
            matched_title = match.group(1)
            target_slug = self.registry_lower.get(matched_title.lower())
            if not target_slug:
                return match.group(0)
                
            # Safeguard 1: Don't link a topic to itself or its alternative titles
            if target_slug == slug or matched_title in current_titles:
                return match.group(0)
                
            # Safeguard 2: Don't link to a main parent module if we are already in its shard
            if target_slug in parents:
                return match.group(0)
                
            # Ensure it's not already linked in this node
            if target_slug in linked_in_node:
                return match.group(0)
                
            # Ensure it is not already inside a link tag
            if is_inside_link(match.start()):
                return match.group(0)
                
            # SEMANTIC COLLISION SAFEGUARD:
            if matched_title in self.TERM_ANCHORS:
                anchors = self.TERM_ANCHORS[matched_title]
                text_lower = masked_content.lower()
                if not any(anchor in text_lower for anchor in anchors):
                    return match.group(0) # Skip if no technical context found

            # Determine URL and class
            if target_slug in self.data["topic_contents"]:
                url = f"/physics/topic/{target_slug}"
                link_class = "topic-link"
            else:
                url = f"/physics/subtopic/{target_slug}"
                link_class = "subtopic-link"

            link_html = f'<a href="{url}" class="{link_class}"><strong>{matched_title}</strong></a>'
            linked_in_node.add(target_slug)
            return link_html

        masked_content = self.compiled_plain_regex.sub(replace_plain, masked_content)
        
        final_content = self.unmask_mathjax(masked_content, placeholders)
        final_content = self._sanitize_mathjax(final_content)

        # Visual Integrity Fix: Strip links from headers generated by the auto-linker
        def clean_header(match):
            header_html = match.group(0)
            if '<a' in header_html.lower():
                clean_html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', header_html)
                return clean_html
            return header_html
            
        final_content = re.sub(r'<h[34][^>]*>.*?</h[34]>', clean_header, final_content, flags=re.IGNORECASE | re.DOTALL)

        if not dry_run:
            topic["content"] = final_content
            
        return final_content if final_content != original_content else None

    def _apply_entity_links(self, content, current_slug=None):
        """Internal helper to link entities from entities.json."""
        for e_id, e_data in self.data.get("entities", {}).items():
            link = e_data["link"]
            # Only link if not already linked to this entity (exact href check)
            if f'href="{link}"' in content: continue
            
            # Safeguard: Don't link to itself
            if current_slug:
                if link == f"/physics/subtopic/{current_slug}" or link == f"/physics/topic/{current_slug}":
                    continue

            variants = [e_data["name"]] + e_data.get("aliases", [])
            # Sort by length descending to match longest first
            variants.sort(key=len, reverse=True)
            
            for var in variants:
                if len(var) < 3: continue
                # Match name not preceded by > or =
                pattern = re.compile(rf'(?<![=">])\b{re.escape(var)}\b', re.IGNORECASE)
                if pattern.search(content):
                    link_html = f'<a href="{link}" class="subtopic-link"><strong>{var}</strong></a>'
                    content = pattern.sub(lambda m: link_html, content)
                    break # Only link the first match of any variant
        return content

    def _sanitize_mathjax(self, content):
        content = content.replace(" > ", " \\gt ")
        content = content.replace(" < ", " \\lt ")
        return content

    def _validate_slug_and_title(self, slug, title):
        """Centralized check for protected slugs and titles."""
        # 1. Protected Slug Check
        if slug in self.PROTECTED_TOPICS:
            return False, f"Slug [{slug}] is a PROTECTED main topic."
        
        # 2. Title Collision Check (prevent subtopics with titles that are main topics)
        # Normalize title to slug-like form for comparison
        norm_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        if norm_title in self.PROTECTED_TOPICS:
            return False, f"Title '{title}' corresponds to a PROTECTED main topic slug [{norm_title}]."
        
        # 3. Registry Conflict Check (is this title already used for a main topic?)
        if title in self.registry:
            existing_slug = self.registry[title]
            if existing_slug in self.PROTECTED_TOPICS:
                return False, f"Title '{title}' is already assigned to PROTECTED main topic [{existing_slug}]."

        return True, None

    def add_subtopic(self, slug, subtopic_data, link_in_parent=True):
        """Adds subtopic to appropriate shard and updates registry. Prevents duplicates."""
        # Safeguard: Prevent overwriting protected main topics or title collisions
        ok, error = self._validate_slug_and_title(slug, subtopic_data.get("title", ""))
        if not ok:
            print(f"ERROR: {error} Cannot add subtopic.")
            return False

        # 1. Mandatory Global Duplicate Check
        if slug in self.data["subtopics"]:
            existing_shard = self.slug_to_shard.get(slug, "Unknown")
            print(f"WARNING: Slug [{slug}] already exists in {existing_shard}. Merging/Updating instead.")
            shard_file = existing_shard
        else:
            parent_slug = subtopic_data.get("parents", ["misc"])[0]
            shard_file = f"{parent_slug}.json"
            if parent_slug in self.data["subtopics"]:
                shard_file = self.slug_to_shard.get(parent_slug, shard_file)
        
        if shard_file not in self.shards:
            self.shards[shard_file] = {}
        
        self.shards[shard_file][slug] = subtopic_data
        self.data["subtopics"][slug] = subtopic_data
        self.slug_to_shard[slug] = shard_file
        self.registry[subtopic_data["title"]] = slug
        self.modified_slugs.add(slug) # MARK AS DIRTY
        self._refresh_sorted_titles()
        self.apply_auto_links(slug)

        # 2. Platinum Certification Loop
        final_content = self.data["subtopics"][slug].get("content", "")
        if self.validate_platinum_standard(slug, final_content):
            self.data["subtopics"][slug]["standard"] = "platinum"
            print(f"CERTIFIED PLATINUM: [{slug}]")
        else:
            self.data["subtopics"][slug]["standard"] = "legacy"

        return True

    def update_subtopic(self, slug, subtopic_data):
        """Safely updates an existing subtopic."""
        if slug not in self.data["subtopics"]:
            print(f"ERROR: Subtopic [{slug}] does not exist. Use add_subtopic instead.")
            return False
            
        if slug in self.PROTECTED_TOPICS:
            print(f"ERROR: Cannot update PROTECTED main topic [{slug}] via update_subtopic.")
            return False
            
        # Check if title changed and if new title collides
        new_title = subtopic_data.get("title")
        if new_title:
            ok, error = self._validate_slug_and_title(slug, new_title)
            if not ok:
                print(f"ERROR: {error}")
                return False

        shard_file = self.slug_to_shard[slug]
        self.shards[shard_file][slug] = subtopic_data
        self.data["subtopics"][slug] = subtopic_data
        self.modified_slugs.add(slug) # MARK AS DIRTY
        
        if new_title:
            # Update registry if title changed
            old_title = next((t for t, s in self.registry.items() if s == slug), None)
            if old_title and old_title != new_title:
                del self.registry[old_title]
            self.registry[new_title] = slug
            self._refresh_sorted_titles()
            
        self.apply_auto_links(slug)

        # 2. Platinum Certification Loop
        # We re-fetch content from self.data because apply_auto_links modifies it in-place
        final_content = self.data["subtopics"][slug].get("content", "")
        if self.validate_platinum_standard(slug, final_content):
            self.data["subtopics"][slug]["standard"] = "platinum"
            print(f"CERTIFIED PLATINUM: [{slug}]")
        else:
            self.data["subtopics"][slug]["standard"] = "legacy"

        return True

    def delete_subtopic(self, slug):
        """Safely removes a subtopic from its shard and the registry."""
        if slug in self.PROTECTED_TOPICS:
            print(f"ERROR: Cannot delete PROTECTED main topic [{slug}].")
            return False
            
        if slug not in self.data["subtopics"]:
            print(f"ERROR: Subtopic [{slug}] not found.")
            return False
            
        shard_file = self.slug_to_shard.get(slug)
        if shard_file and slug in self.shards.get(shard_file, {}):
            del self.shards[shard_file][slug]
            
        if slug in self.data["subtopics"]:
            del self.data["subtopics"][slug]
            
        title = next((t for t, s in self.registry.items() if s == slug), None)
        if title:
            del self.registry[title]
            
        if slug in self.slug_to_shard:
            del self.slug_to_shard[slug]
            
        self._refresh_sorted_titles()
        print(f"✓ Subtopic [{slug}] deleted from {shard_file}.")
        return True

    def ingest_subtopic_platinum(self, slug, subtopic_data):
        """Atomsically adds a subtopic and its local formulas to the registry, returning final IDs."""
        # 1. Extract and register local formulas
        final_ids = subtopic_data.get("formula_ids", [])
        if "formulas" in subtopic_data:
            for f_obj in subtopic_data["formulas"]:
                f_id = self.add_formula(
                    f_obj.get("title"),
                    f_obj.get("equation"),
                    f_obj.get("interpretation") or f_obj.get("breakdown")
                )
                final_ids.append(f_id)
            del subtopic_data["formulas"]
        
        subtopic_data["formula_ids"] = list(set(final_ids))
        
        # 2. Hand over to standard sharding logic
        return self.add_subtopic(slug, subtopic_data)

    def add_formula(self, title, equation, interpretation):
        """Adds a formula to the registry and returns its ID."""
        slug_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        eq_hash = hashlib.md5(equation.encode()).hexdigest()[:8]
        f_id = f"{slug_title}-{eq_hash}"
        
        self.data["formula_registry"][f_id] = {
            "title": title,
            "equation": equation,
            "semantic_variables": {},
            "interpretation": interpretation,
            "symmetry_origin": "Great Expansion: Derivation pending.",
            "limits_and_boundary": "Great Expansion: Boundary analysis pending.",
            "status": "platinum-draft"
        }
        return f_id

    @staticmethod
    def _render_page(url, output_path):
        """Helper to render a URL via curl and save to output_path."""
        try:
            # We use a longer timeout for complex hubs
            timeout = 15 if "/topic/" in url else 10
            result = subprocess.run(["curl", "-s", "-L", url], capture_output=True, text=True, timeout=timeout)
            if result.stdout:
                with open(output_path, "w") as f:
                    f.write(result.stdout)
                return True
        except Exception as e:
            # Silence expected timeout during parallel floods, but log serious ones
            pass
        return False

    def build(self, force=False, slug=None):
        """Pre-renders all subtopics and hubs into static HTML. Parallelized for performance."""
        if slug:
            print(f"Surgically building: {slug}...")
            # Use the environment-aware base URL
            base_url = "http://localhost:8000"
            if slug in self.data["subtopics"]:
                self._render_page(f"{base_url}/physics/subtopic/{slug}?build_mode=1", f"public/cache/subtopic/{slug}.html")
            elif slug in self.data["topics"]:
                self._render_page(f"{base_url}/physics/topic/{slug}?build_mode=1", f"public/cache/topic/{slug}.html")
            else:
                print(f"ERROR: Slug [{slug}] not found in topics or subtopics.")
            return

        print(f"Starting Parallel Static Build {'(FORCE)' if force else '(Shard-Incremental)'}...")
        
        # 1. Build Subtopics
        sub_dir = "public/cache/subtopic"
        if not os.path.exists(sub_dir): os.makedirs(sub_dir)
            
        render_tasks = []
        manifest_updates = {}
        
        for rel_path, sub_slugs in self.shard_to_slugs.items():
            shard_path = os.path.join(self.content_dir, rel_path)
            current_hash = self.get_file_hash(shard_path)
            
            if not force and self.build_manifest.get(f"shard_{rel_path}") == current_hash:
                all_exist = True
                for s in sub_slugs:
                    if not os.path.exists(os.path.join(sub_dir, f"{s}.html")):
                        all_exist = False
                        break
                if all_exist:
                    continue

            # Shard is dirty or missing files
            for s in sub_slugs:
                sub = self.data["subtopics"][s]
                content_str = json.dumps({
                    "t": sub.get("title"), "c": sub.get("content"),
                    "s": sub.get("snippet_svg"), "h": sub.get("hero_math")
                }, sort_keys=True)
                item_hash = hashlib.md5(content_str.encode()).hexdigest()

                if not force and self.build_manifest.get(f"subtopic_{s}") == item_hash and os.path.exists(os.path.join(sub_dir, f"{s}.html")):
                    continue

                url = f"http://localhost:8000/physics/subtopic/{s}?build_mode=1"
                path = os.path.join(sub_dir, f"{s}.html")
                render_tasks.append((url, path, f"subtopic_{s}", item_hash))
            
            # Record that this shard's hash should be updated after processing
            manifest_updates[f"shard_{rel_path}"] = current_hash

        # 2. Build Topic Hubs
        hub_dir = "public/cache/topic"
        if not os.path.exists(hub_dir): os.makedirs(hub_dir)
            
        for hub_slug in self.data["topics"]:
            topic = self.data["topics"][hub_slug]
            shard = self.topic_shards.get(hub_slug, topic)
            hub_str = json.dumps({
                "t": shard.get("title"), "i": shard.get("intro"), "p": shard.get("pillars"),
                "b": shard.get("bridges"), "f": shard.get("field"), "d": shard.get("density")
            }, sort_keys=True)
            new_hash = hashlib.md5(hub_str.encode()).hexdigest()

            if not force and self.build_manifest.get(f"hub_{hub_slug}") == new_hash and os.path.exists(os.path.join(hub_dir, f"{hub_slug}.html")):
                continue

            url = f"http://localhost:8000/physics/topic/{hub_slug}?build_mode=1"
            path = os.path.join(hub_dir, f"{hub_slug}.html")
            render_tasks.append((url, path, f"hub_{hub_slug}", new_hash))

        # 3. Execute Render Tasks in Parallel
        if not render_tasks:
            print("Everything up to date. No pages to build.")
            return

        print(f"Executing {len(render_tasks)} render tasks across {cpu_count()} cores...")
        
        success_count = 0
        with Pool(processes=cpu_count()) as pool:
            # Map the static render function
            results = pool.starmap(self._parallel_worker, render_tasks)
            
            for i, result in enumerate(results):
                if result:
                    _, _, manifest_key, item_hash = render_tasks[i]
                    self.build_manifest[manifest_key] = item_hash
                    success_count += 1

        # Apply Shard Updates
        for k, v in manifest_updates.items():
            self.build_manifest[k] = v

        # Save Manifest
        with open(self.build_manifest_path, "w") as f:
            json.dump(self.build_manifest, f, indent=4)

        print(f"\nSUCCESS: Parallel build complete. Built: {success_count}, Total Tasks: {len(render_tasks)}")

    @staticmethod
    def _parallel_worker(url, path, key, item_hash):
        """Picklable worker function for the pool."""
        return PhysicsOrchestrator._render_page(url, path)

    def get_pillar_context(self, slug):
        """Finds the position of a slug within its parent Hub roadmaps."""
        context = {
            "parent_hub": None,
            "current_pillar": None,
            "next_slug": None,
            "prev_slug": None,
            "neighbors": []
        }
        
        for hub_slug, hub_data in self.topic_shards.items():
            for pillar in hub_data.get("pillars", []):
                slugs = pillar.get("slugs", [])
                if slug in slugs:
                    idx = slugs.index(slug)
                    context["parent_hub"] = hub_data["title"]
                    context["current_pillar"] = pillar["title"]
                    context["neighbors"] = slugs
                    if idx > 0:
                        context["prev_slug"] = slugs[idx-1]
                    if idx < len(slugs) - 1:
                        context["next_slug"] = slugs[idx+1]
                    return context
        return context

    # Broad Technical Anchors used for Context Affinity Scoring
    HUB_SIGNATURES = {
        "relativity": ["relativity", "lorentz", "invariance", "manifold", "metric", "interval", "curvature", "spacetime", "covariant"],
        "classical-mechanics": ["mechanics", "newton", "lagrangian", "hamiltonian", "action", "symmetry", "momentum", "constraint", "geodesic", "inertia"],
        "quantum-physics": ["quantum", "wavefunction", "operator", "hilbert", "uncertainty", "superposition", "quanta", "eigenstate", "unitary"],
        "standard-model": ["standard model", "gauge", "boson", "fermion", "symmetry", "field", "coupling", "renormalization", "flavor", "spinor"],
        "astrophysics": ["astrophysics", "astronomy", "luminosity", "stellar", "galaxy", "collapse", "degenerate", "accretion", "redshift", "horizon"],
        "thermodynamics-statistical-mechanics": ["thermodynamics", "entropy", "partition", "statistical", "ensemble", "temperature", "equilibrium", "boltzmann"]
    }

    def sanitize_content(self, html):
        """Self-healing function to fix trivial formatting errors before validation."""
        original_html = html
        
        # 1. Purge links from headers (Visual Integrity Fix)
        def clean_header(match):
            header_html = match.group(0)
            if '<a' in header_html.lower():
                clean_html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', header_html)
                print(f"  [Self-Healing] Purged link from header: {clean_html}")
                return clean_html
            return header_html
            
        html = re.sub(r'<h[34][^>]*>.*?</h[34]>', clean_header, html, flags=re.IGNORECASE | re.DOTALL)
        
        # 2. Purge forbidden meta-talk
        forbidden_phrases = [
            ("university-level", "theoretical"),
            ("imagine a world", "consider a system"),
            ("in conclusion", ""),
            ("let's dive into", "we analyze"),
            ("as we have seen", "")
        ]
        
        for bad, good in forbidden_phrases:
            if re.search(rf'\b{bad}\b', html, flags=re.IGNORECASE):
                print(f"  [Self-Healing] Replaced forbidden meta-talk '{bad}' with '{good}'.")
                html = re.sub(rf'\b{bad}\b', good, html, flags=re.IGNORECASE)
                
        return html

    def validate_platinum_standard(self, slug, html):
        """Enforces the Organic Platinum Standard with Semantic Signature Enforcement."""
        errors = []
        text_only = re.sub(r'<.*?>', '', html).lower()
        word_count = len(text_only.split())
        
        # 1. Structural Checks
        if word_count < 650:
            errors.append(f"Technical Density Failure: {word_count} words (Target: 650+).")

        headers = re.findall(r'<h[34][^>]*>.*?</h[34]>', html, re.IGNORECASE | re.DOTALL)
        for h in headers:
            if "<a" in h.lower():
                errors.append(f"Visual Integrity Violation: Links found in header {h}.")

        if any(char in html for char in ['\b', '\a', '\f', '\v']):
            errors.append("Mathematical Sanity Failure: Mangled control characters detected.")

        # 2. Topological Link Analysis
        links = re.findall(r'href="/physics/(subtopic|topic)/([^"]*)"', html)
        if len(links) < 5:
            errors.append(f"Graph Connectivity Failure: Only {len(links)} links found (Target: 5+).")
        
        # Check for duplicate links (Single Link Rule)
        seen_links = set()
        for l in links:
            if l in seen_links:
                errors.append(f"Navigation Clutter: Duplicate link to [{l}] found.")
            seen_links.add(l)

        # 3. Semantic Signature Enforcement (Context Integrity)
        sub = self.data["subtopics"].get(slug, {})
        parents = sub.get("parents", [])
        
        # Recursive Hub Resolution: find which Gateway Hub(s) this topic ultimately belongs to
        resolved_hubs = set()
        queue = list(parents)
        visited = set()
        while queue:
            p = queue.pop(0)
            if p in visited: continue
            visited.add(p)
            if p in self.HUB_SIGNATURES:
                resolved_hubs.add(p)
            else:
                # Check if this parent is itself a subtopic with its own parents
                parent_sub = self.data["subtopics"].get(p)
                if parent_sub and "parents" in parent_sub:
                    queue.extend(parent_sub["parents"])

        # Calculate affinity for all hubs
        scores = {}
        for hub, signature in self.HUB_SIGNATURES.items():
            count = sum(1 for word in signature if word in text_only)
            scores[hub] = count

        # Must have highest affinity for parent hub
        for p in resolved_hubs:
            parent_score = scores.get(p, 0)
            # Find if any other hub is outscoring the parent (Contextual Leakage)
            for other_hub, other_score in scores.items():
                if other_hub != p and other_score > parent_score + 2:
                     errors.append(f"Contextual Leakage: Topic [{slug}] for Hub [{p}] has higher semantic affinity for [{other_hub}].")
            
            if parent_score < 2:
                errors.append(f"Theoretical Signal Loss: Content lacks foundational vocabulary for Hub [{p}].")

        # 4. In Media Res Lead Check
        title = sub.get("title", "").lower()
        title_words = [w for w in title.split() if len(w) > 3]
        first_p_match = re.search(r'<p>(.*?)</p>', html, re.DOTALL)
        if first_p_match:
            first_p = first_p_match.group(1)
            # Strip tags for check
            first_p_text = re.sub(r'<.*?>', '', first_p).lower()
            first_sentence = re.split(r'[.!?]', first_p_text)[0]
            if any(word in first_sentence for word in title_words):
                errors.append(f"Standard Violation: Lead sentence is self-referential (contains title words).")

        # 5. Context Integrity: Title-Slug Dissonance
        title = sub.get("title", "")
        if title:
            # Generalized specificity markers
            markers = ["qft", "quantum field theory", "general-relativity", "special-relativity", "quantum", "classical", "statistical"]
            for m in markers:
                m_slug = m.replace(" ", "-")
                if m_slug in slug.lower() and m not in title.lower():
                    errors.append(f"Context Dissonance: Slug implies [{m}], but Title [{title}] is generic.")
                if m in title.lower() and m_slug not in slug.lower() and m.replace(" ", "") not in slug.lower():
                    errors.append(f"Context Dissonance: Title implies [{m}], but Slug [{slug}] is generic.")

        # 5. Implicit Authority: Forbidden Meta-Talk
        meta_ban = ["university-level", "advanced topics", "this section discusses", "this investigation", "in conclusion"]
        for phrase in meta_ban:
            if phrase in text_only:
                errors.append(f"Implicit Authority Violation: Forbidden meta-talk detected: '{phrase}'.")

        # 6. Linguistic Artifact Scrubber (Anti-Fluff)
        ban_phrases = ["imagine a world", "in the realm of", "journey through", "tapestry of", "it is important to note"]
        for phrase in ban_phrases:
            if phrase in text_only:
                errors.append(f"Linguistic Artifact: '{phrase}' (AI Fluff).")

        if errors:
            self.last_validation_errors = errors
            print(f"PLATINUM VALIDATION FAILED for [{slug}]:")
            for e in errors:
                print(f"  - {e}")
            return False
        
        self.last_validation_errors = []
        print(f"✓ Platinum Validation Passed for [{slug}] ({word_count} words).")
        return True

    def update_formula(self, formula_id, data):
        """Surgically updates an entry in the global formulas.json registry."""
        if formula_id not in self.data["formula_registry"]:
            print(f"WARNING: Formula ID [{formula_id}] not found. Creating new entry.")
            self.data["formula_registry"][formula_id] = {}
        
        # Merge data
        for key, value in data.items():
            self.data["formula_registry"][formula_id][key] = value
        
        # Ensure status is platinum if we are beefing it up
        self.data["formula_registry"][formula_id]["status"] = "platinum"
        print(f"SUCCESS: Updated formula [{formula_id}]. Run save() to persist.")

    def deploy_change(self, slug, build_hub=True):
        """Unified workflow to save, build, and sync a single concept change."""
        print(f"Deploying change for: {slug}...")
        # 1. Clear snippets and force regeneration for this slug
        if slug in self.data["subtopics"]:
            self.data["subtopics"][slug].pop('snippet', None)
            self.data["subtopics"][slug].pop('snippet_svg', None)
            self.data["subtopics"][slug].pop('hero_math', None)
            self.modified_slugs.add(slug) # MARK AS DIRTY for save()
        
        # 2. Save modified shards
        self.save(auto_commit=False, unlock_protected=True)
        
        # 3. Surgical Build
        self.build(slug=slug)
        
        # 4. Optional Hub Rebuild
        if build_hub:
            # Find parent topic
            parents = []
            if slug in self.data["subtopics"]:
                parents = self.data["subtopics"][slug].get("parents", [])
            for p in parents:
                if p in self.data["topics"]:
                    self.build(slug=p)
        
        # 5. CLI Sync
        subprocess.run(["php", "cli_sync.php"], capture_output=True)
        print(f"SUCCESS: [{slug}] is now live in the static cache.")

    def audit_registry(self):
        """Analyzes the slug registry for identity collisions and linguistic divergence."""
        print("Starting Registry Identity Audit...")
        
        # 1. Reverse the registry: Slug -> [Titles]
        slug_map = {}
        for title, slug in self.registry.items():
            if slug not in slug_map:
                slug_map[slug] = []
            slug_map[slug].append(title)
        
        collisions = []
        for slug, titles in slug_map.items():
            if len(titles) > 1:
                # Calculate basic divergence
                # If titles are very different lengths or words don't overlap, flag high risk
                base_title = titles[0].lower()
                for t in titles[1:]:
                    words_base = set(re.findall(r'\w+', base_title))
                    words_other = set(re.findall(r'\w+', t.lower()))
                    
                    overlap = len(words_base.intersection(words_other))
                    union = len(words_base.union(words_other))
                    similarity = overlap / union if union > 0 else 0
                    
                    if similarity < 0.4:
                        collisions.append({
                            "slug": slug,
                            "titles": titles,
                            "similarity": similarity,
                            "risk": "HIGH"
                        })
                    elif similarity < 0.8:
                        collisions.append({
                            "slug": slug,
                            "titles": titles,
                            "similarity": similarity,
                            "risk": "MEDIUM (Alias?)"
                        })

        # 2. Output Report
        print(f"\n--- REGISTRY AUDIT REPORT ---")
        print(f"Total Slugs Analyzed: {len(slug_map)}")
        print(f"Total Multi-Title Slugs: {sum(1 for t in slug_map.values() if len(t) > 1)}")
        print(f"Potential Collisions Detected: {len(collisions)}")
        print(f"-----------------------------")
        
        high_risk = [c for c in collisions if c["risk"] == "HIGH"]
        if high_risk:
            print(f"\n[HIGH RISK] Identity Collisions (Low Linguistic Overlap):")
            for c in high_risk:
                print(f"  - [{c['slug']}]: {', '.join(c['titles'])} (Sim: {c['similarity']:.2f})")
                
        medium_risk = [c for c in collisions if "MEDIUM" in c["risk"]]
        if medium_risk:
             print(f"\n[MEDIUM RISK] Potential Aliases (Review Required):")
             for c in medium_risk[:10]: # Cap at 10 for summary
                 print(f"  - [{c['slug']}]: {', '.join(c['titles'])} (Sim: {c['similarity']:.2f})")
        
        return collisions

    def audit(self):
        """Performs a deep technical audit of all subtopics and hubs."""
        print("Starting Platinum Audit...")
        report = {
            "low_density": [], # < 500 words
            "missing_math": [], # No LaTeX delimiters
            "missing_hero": [], # No hero math
            "total_words": 0,
            "total_subtopics": len(self.data["subtopics"])
        }

        for slug, sub in self.data["subtopics"].items():
            content = sub.get("content", "")
            
            # 1. Word Count
            text_only = re.sub(r'<.*?>', '', content)
            words = text_only.split()
            word_count = len(words)
            report["total_words"] += word_count
            
            if word_count < 500:
                report["low_density"].append((slug, word_count))
            
            # 2. Math Check
            if not (re.search(r'\\+\(', content) or re.search(r'\\+\[', content)):
                report["missing_math"].append(slug)
                
            # 3. Hero Check
            if not sub.get("hero_math"):
                report["missing_hero"].append(slug)

        # Print Summary
        print(f"\n--- AUDIT REPORT ---")
        print(f"Total Subtopics: {report['total_subtopics']}")
        print(f"Total Word Count: {report['total_words']:,}")
        print(f"Average Words/Topic: {int(report['total_words']/report['total_subtopics'])}")
        print(f"--------------------")
        print(f"Low Density Topics (< 500 words): {len(report['low_density'])}")
        print(f"Missing Math: {len(report['missing_math'])}")
        print(f"Missing Hero Math: {len(report['missing_hero'])}")
        
        if report["low_density"]:
            print(f"\nTop 10 Thinnest Topics:")
            sorted_thin = sorted(report["low_density"], key=lambda x: x[1])
            for slug, count in sorted_thin[:10]:
                print(f"  - [{slug}]: {count} words")

        return report

    def validate(self):
        print("Running Integrity Shield...")
        result = subprocess.run(["python3", "integrity_shield.py"], capture_output=True, text=True)
        print(result.stdout)
        return result.returncode == 0

if __name__ == "__main__":
    orchestrator = PhysicsOrchestrator()
    print(f"Orchestrator ready. {len(orchestrator.data['subtopics'])} subtopics loaded from shards.")
    print(f"Main topics sharded: {len(orchestrator.topic_shards)}")
