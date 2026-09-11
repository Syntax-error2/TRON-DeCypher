import os
path = r'app\knowledge\dictionaries\ctf_tron_context.txt'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
    
new_words = "neon\ncircuit\ndefense\nnetwork\nforensics\ncyber\nstego\n"
if not content.startswith(new_words):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_words + content)
