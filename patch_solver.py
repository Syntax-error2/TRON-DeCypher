with open('app/decoders/symbols/solver.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('if "CTF{" in text or "FLAG{" in text or "TRON{" in text:', 'if "CTK{" in text or "FLAG{" in text or "TRON{" in text or "CTF{" in text:')
content = content.replace('if "CTF{" in text: score += 5.0', 'if "CTK{" in text or "CTF{" in text: score += 5.0')

with open('app/decoders/symbols/solver.py', 'w', encoding='utf-8') as f:
    f.write(content)
