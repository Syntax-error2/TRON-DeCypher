import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('self.btn_preview.clicked.connect(self.preview_candidates)', 'pass # self.btn_preview.clicked.connect(self.preview_candidates)')

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
