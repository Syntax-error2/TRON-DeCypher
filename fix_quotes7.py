with open('app/ui/views/decoder_view.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('replace("<b>", "").replace("</b>", "")\n', 'replace("<b>", "").replace("</b>", ""))\n')
with open('app/ui/views/decoder_view.py', 'w', encoding='utf8') as f:
    f.write(content)
