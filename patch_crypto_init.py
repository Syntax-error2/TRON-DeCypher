with open('tests/qa/test_crypto_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from app.decoders import decoder_registry', 'from app.decoders import decoder_registry, register_all_decoders\nregister_all_decoders()')

with open('tests/qa/test_crypto_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
