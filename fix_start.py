import re

with open('app/ui/views/decoder_view.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('self._start_hash_recovery()', 'self.inline_start_recovery()')

with open('app/ui/views/decoder_view.py', 'w', encoding='utf8') as f:
    f.write(content)
