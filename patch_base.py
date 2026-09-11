with open('app/decoders/core/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("FLAG_PATTERN = re.compile(r'^(CTF|FLAG|TRON|HTB|THM)\{(.*?)\}$', re.IGNORECASE)", "FLAG_PATTERN = re.compile(r'^(CTK|FLAG|TRON|CTF|HTB|THM)\{(.*?)\}$', re.IGNORECASE)")

with open('app/decoders/core/base.py', 'w', encoding='utf-8') as f:
    f.write(content)
