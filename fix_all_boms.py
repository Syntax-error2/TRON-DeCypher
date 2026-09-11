with open('app/ui/views/decoder_view.py', 'rb') as f:
    content = f.read()

content = content.replace(b'\xef\xbb\xbf', b'')

with open('app/ui/views/decoder_view.py', 'wb') as f:
    f.write(content)
