import re

def test_regex():
    # content = r"total work \( W \) performed"
    # In the JSON shard it is \\( W \\)
    content = "total work \\\\( W \\\\) performed"
    print(f"Content: {repr(content)}")
    
    math_blocks = []
    def mask_math(match):
        print(f"Match: {repr(match.group(0))}")
        print(f"Group 1: {repr(match.group(1))}")
        math_blocks.append((match.group(1), match.group(0)))
        return f"___MATH_BLOCK_{len(math_blocks)-1}___"

    masked = re.sub(r'\\{1,2}\[(.*?)\\{1,2}\]', mask_math, content, flags=re.DOTALL)
    masked = re.sub(r'\\{1,2}\((.*?)\\{1,2}\)', mask_math, masked, flags=re.DOTALL)
    
    print(f"Masked: {masked}")
    print(f"Blocks: {math_blocks}")

if __name__ == "__main__":
    test_regex()
