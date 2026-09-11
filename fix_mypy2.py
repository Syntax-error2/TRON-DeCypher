with open('app/crypto/hashes/hash_identifier.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('    def __init__(self):', '    def __init__(self) -> None:')
with open('app/crypto/hashes/hash_identifier.py', 'w', encoding='utf8') as f:
    f.write(content)
