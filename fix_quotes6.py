with open('app/ui/views/decoder_view.py', 'r', encoding='utf8') as f:
    content = f.read()

import re
content = content.replace('replace("<b>", ").replace("</b>", "))', 'replace("<b>", "").replace("</b>", "")')
content = content.replace('replace("<b>", ").replace("</b>", ")', 'replace("<b>", "").replace("</b>", "")')
with open('app/ui/views/decoder_view.py', 'w', encoding='utf8') as f:
    f.write(content)
