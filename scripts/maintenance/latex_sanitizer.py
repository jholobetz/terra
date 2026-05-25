import re

def sanitize_latex(equation_str):
    """Sanitizes raw LaTeX strings to prevent MathJax parsing failures.
    
    1. Fixes double-escaped or backslash-escaped single and double quotes (e.g., \\' -> ')
    2. Translates text-mode commands like \\AA or \\text{\\AA} to MathJax-compatible math-mode equivalents.
    """
    if not equation_str or not isinstance(equation_str, str):
        return equation_str

    # 1. Fix escaped quotes that occur during JSON serialization or shell passes
    sanitized = equation_str.replace("\\'", "'")
    sanitized = sanitized.replace('\\"', '"')

    # 2. Fix unsupported text-mode Ångström command: \text{\AA} or \AA -> \text{Å}
    # Match both \text{\AA} and \AA case-sensitively
    sanitized = re.sub(r'\\text\{\s*\\AA\s*\}', '\\\\text{Å}', sanitized)
    sanitized = re.sub(r'\\AA', '\\\\text{Å}', sanitized)

    return sanitized
