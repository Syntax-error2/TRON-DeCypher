import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('res_str = f"o" RECOVERED\\\\nValue: {c}"', 'res_str = f"✅ RECOVERED\\\\nValue: {c}"')
content = content.replace('res_str = f"o" RECOVERED\\nValue: {c}"', 'res_str = f"✅ RECOVERED\\nValue: {c}"')

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
