import re

def sanitize_latex(equation_str):
    """Sanitizes raw LaTeX strings to prevent MathJax parsing failures.
    
    1. Fixes double-escaped or backslash-escaped single and double quotes (e.g., \\' -> ')
    2. Translates text-mode commands like \\AA or \\text{\\AA} to MathJax-compatible math-mode equivalents.
    3. Cleans double-escaped backslashes before standard LaTeX commands (e.g., \\mu -> \mu).
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

    # 3. Fix double-escaped backslashes before LaTeX commands (e.g. \\mu -> \mu, \\left -> \left)
    # A double backslash followed by a letter is always a double-escaped single backslash in math mode.
    # We match 2 or more backslashes followed by a letter and replace them with a single backslash.
    sanitized = re.sub(r'\\{2,}([a-zA-Z])', r'\\\1', sanitized)

    return sanitized

