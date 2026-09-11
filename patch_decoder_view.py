with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('marker = " [FLAG CANDIDATE]" if "CTF{" in c[\'text\'] or "FLAG{" in c[\'text\'] or "TRON{" in c[\'text\'] else ""', 'marker = " 🚩 FLAG CANDIDATE" if "CTK{" in c[\'text\'] or "CTF{" in c[\'text\'] or "FLAG{" in c[\'text\'] or "TRON{" in c[\'text\'] else ""')

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
