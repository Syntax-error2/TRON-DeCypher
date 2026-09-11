with open('app/knowledge/challenge_context.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('["TRON{...}", "FLAG{...}", "CTF{...}"]', '["CTK{...}", "FLAG{...}", "TRON{...}", "CTF{...}"]')
with open('app/knowledge/challenge_context.py', 'w', encoding='utf-8') as f:
    f.write(content)
