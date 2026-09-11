with open('app/knowledge/flag_detection.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('self.default_patterns = [r"CTF\{.*?\}", r"TRON\{.*?\}", r"FLAG\{.*?\}"]', 'self.default_patterns = [r"CTK\{.*?\}", r"FLAG\{.*?\}", r"TRON\{.*?\}", r"CTF\{.*?\}"]')

with open('app/knowledge/flag_detection.py', 'w', encoding='utf-8') as f:
    f.write(content)
