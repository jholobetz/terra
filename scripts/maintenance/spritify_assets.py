import os
import sys

# Re-direct to despritify_assets.py to keep the codebase robust and un-spritified
from despritify_assets import main as despritify_main

def main():
    print("⚠️  spritify_assets.py has been deprecated in favor of robust, fully-inlined, self-contained SVG rendering.")
    print("   This ensures 100% cross-browser compatibility (specifically resolving Safari/WebKit rendering bugs).")
    print("   Running de-spritification to ensure all JSON files are cleanly restored...")
    
    # Run the de-spritify script
    despritify_main()
    
    # Clean up math_sprites.svg files if they exist
    paths_to_remove = ["public/math_sprites.svg", "app/config/content/math_sprites.svg"]
    for path in paths_to_remove:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Removed deprecated sprite sheet: {path}")
            except Exception as e:
                print(f"Could not remove {path}: {e}")

if __name__ == "__main__":
    # Add parent directory or maintenance directory to path to import despritify_assets
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()
