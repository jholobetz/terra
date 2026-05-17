import re

def test_balanced_regex():
    content = r"The formula is \[ W = \int \left[ \frac{1}{2}mv^2 \right] \] and it works."
    print(f"Content: {content}")
    
    # 1. Non-greedy (The buggy one)
    match_buggy = re.search(r'\\{1,2}\[(.*?)\\{1,2}\]', content)
    print(f"Buggy match: {match_buggy.group(1) if match_buggy else 'None'}")
    
    # 2. Lookbehind fix
    # We want to match \] only if NOT preceded by \right
    match_fixed = re.search(r'\\{1,2}\[(.*?)(?<!\\right)\\{1,2}\]', content)
    print(f"Fixed match: {match_fixed.group(1) if match_fixed else 'None'}")

if __name__ == "__main__":
    test_balanced_regex()
