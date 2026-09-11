with open('tests/unit/test_decoder_expansion.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('assert "md5" in [c.algorithm.upper() for c in cands]', 'assert "MD5" in [c.algorithm.upper() for c in cands]')
with open('tests/unit/test_decoder_expansion.py', 'w', encoding='utf8') as f:
    f.write(content)
