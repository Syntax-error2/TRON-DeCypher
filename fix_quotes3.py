with open('app/ui/views/decoder_view.py', 'r', encoding='utf8') as f:
    content = f.read()

import re
content = re.sub(r'data\.get\("candidate", "\)', 'data.get("candidate", "")', content)

with open('app/ui/views/decoder_view.py', 'w', encoding='utf8') as f:
    f.write(content)
