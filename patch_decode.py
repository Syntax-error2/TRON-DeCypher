import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'res = decoder.decode(self._get_input())',
    'res = decoder.decode(self._get_input(), {"case_id": getattr(self, "current_case_id", None)})'
)

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
