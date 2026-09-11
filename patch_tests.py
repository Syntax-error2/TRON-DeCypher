with open('tests/qa/test_decoder_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"XGP{SVIIL}"', '"XGP{SVOOL}"')
content = content.replace('"AABAA BAABA ABABA"', '"AAABA BAABB ABABA"')

with open('tests/qa/test_decoder_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
