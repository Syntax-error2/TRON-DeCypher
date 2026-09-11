with open('tests/qa/test_crypto_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"IFMML", "HELLO"', '"IFMMP", "HELLO"')
content = content.replace('\'{"flag": "CTK{JWT_TEST}", "category": "crypto"}\'', '"CTK{JWT_TEST}"')

with open('tests/qa/test_crypto_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
