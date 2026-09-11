with open('app/ui/views/decoder_view.py', 'r', encoding='utf8') as f:
    content = f.read()

import re
content = content.replace('", "Images', '"", "Images')

with open('app/ui/views/decoder_view.py', 'w', encoding='utf8') as f:
    f.write(content)
