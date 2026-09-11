import re
with open('app/decoders/core/detector.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure MD5/SHA-1/SHA-256 gets priority.
patch = '''
        # 2. Encodings
        for decoder in self.registry.list_all():
            name = decoder.name
            if not getattr(decoder, 'reversible', True):
                continue
            
            try:
                result = decoder.detect(input_data)
                if isinstance(result, tuple):
                    conf, meta = result
                else:
                    conf = result
                    meta = {}
                
                # Suppress generic encodings if we have a strong hash candidate
                if has_strong_hash:
                    if name.lower() in ["hex", "base64", "base32", "url", "html"]:
                        # Cap confidence so they don't override the hash
                        conf = min(conf, 0.4)
                
                if conf > 0:
'''
start_idx = content.find("        # 2. Encodings")
end_idx = content.find("                if conf > 0:") + len("                if conf > 0:")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + patch.strip('\n') + content[end_idx:]
    with open('app/decoders/core/detector.py', 'w', encoding='utf-8') as f:
        f.write(content)
