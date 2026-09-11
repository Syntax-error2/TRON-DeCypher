with open('app/core/config.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('    app_version: str = "1.0.0"', '    app_version: str = "1.0.0"\n    flag_pattern: str = "CTK{...}"')

with open('app/core/config.py', 'w', encoding='utf-8') as f:
    f.write(content)
