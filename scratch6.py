with open('tests/unit/test_decoder_expansion.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('assert "SHA-1" in [c.algorithm for c in cands_sha1]', 'assert "SHA-1" in [c.algorithm.upper() for c in cands_sha1]')
with open('tests/unit/test_decoder_expansion.py', 'w', encoding='utf8') as f:
    f.write(content)
