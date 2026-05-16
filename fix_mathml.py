import json
import re
import os

def fix_latex(text):
    if not text: return text
    # Replace \mathbf{\greek} with \boldsymbol{\greek}
    greek_letters = ['tau', 'omega', 'Omega', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', 'upsilon', 'phi', 'chi', 'psi']
    for letter in greek_letters:
        text = text.replace(f'\\mathbf{{\\{letter}}}', f'\\boldsymbol{{\\{letter}}}')
    return text

files = ['formulas.json', 'classical-mechanics.json', 'relativity.json', 'standard-model.json']
for file in files:
    path = os.path.join('app/config/content', file)
    with open(path, 'r') as f:
        data = json.load(f)
    
    modified = False
    
    if file == 'formulas.json':
        for k, v in data.items():
            eq = v.get('equation', '')
            fixed = fix_latex(eq)
            if fixed != eq:
                v['equation'] = fixed
                modified = True
                print(f"Fixed {k} in formulas.json")
    else:
        for k, v in data.items():
            if isinstance(v, dict) and 'content' in v:
                c = v['content']
                fixed = fix_latex(c)
                if fixed != c:
                    v['content'] = fixed
                    modified = True
                    print(f"Fixed {k} in {file}")

    if modified:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
