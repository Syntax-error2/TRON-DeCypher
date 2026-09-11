with open('app/ui/views/decoder_view.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('f\"\"', 'f\"').replace('\"\"', '\"')
with open('app/ui/views/decoder_view.py', 'w', encoding='utf8') as f:
    f.write(content)
