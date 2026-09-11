with open('app/decoders/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'from app.decoders.classical.polybius_based import PolybiusDecoder, TapCodeDecoder',
    'from app.decoders.classical.polybius_based import PolybiusDecoder, TapCodeDecoder, A1Z26Decoder'
)

content = content.replace(
    '    decoder_registry.register(TapCodeDecoder())',
    '    decoder_registry.register(TapCodeDecoder())\n    decoder_registry.register(A1Z26Decoder())'
)

with open('app/decoders/__init__.py', 'w', encoding='utf-8') as f:
    f.write(content)
