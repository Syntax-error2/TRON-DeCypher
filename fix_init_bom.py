with open('app/decoders/__init__.py', 'rb') as f:
    content = f.read()

if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]

with open('app/decoders/__init__.py', 'wb') as f:
    f.write(content)
