with open('app/crypto/hashes/hash_identifier.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('fmt = hash_format_registry.get(algo)', 'fmt: HashFormat | None = hash_format_registry.get(algo)')
with open('app/crypto/hashes/hash_identifier.py', 'w', encoding='utf8') as f:
    f.write(content)
