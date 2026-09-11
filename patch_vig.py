with open('tests/qa/test_crypto_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('"Vigenre Cipher"', '"Vigenère Cipher"')
with open('tests/qa/test_crypto_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
