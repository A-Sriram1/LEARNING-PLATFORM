# -*- coding: utf-8 -*-
import ast
with open('app/pages.py', encoding='utf-8') as f:
    src = f.read()
tree = ast.parse(src)
funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
assigns = [n.targets[0].id for n in ast.walk(tree) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
print("Functions:", funcs)
print("Module-level assignments:", assigns)

# Check what's missing
needed = ['_WS_CSS', '_ws_panels', '_ws_script']
for name in needed:
    found = name in assigns or name in funcs
    print(f"  {name}: {'OK' if found else 'MISSING'}")
