import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'marker = " .*? FLAG CANDIDATE"', 'marker = " 🚩 CTK FLAG CANDIDATE"', content)

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
