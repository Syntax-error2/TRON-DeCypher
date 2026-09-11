with open('app/decoders/text/text_transforms.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_block = '''            chars = list(set(cleaned))
            if len(chars) > 2:
                return self._create_result(False, errors=["Input contains more than 2 distinct characters."])
            if len(chars) == 2:
                cleaned = cleaned.replace(chars[0], 'a').replace(chars[1], 'b')
            elif len(chars) == 1:
                cleaned = cleaned.replace(chars[0], 'a')'''

good_block = '''            chars = sorted(list(set(cleaned)))
            if len(chars) > 2:
                return self._create_result(False, errors=["Input contains more than 2 distinct characters."])
            
            if not all(c in ('a', 'b') for c in chars):
                if len(chars) == 2:
                    cleaned = cleaned.replace(chars[0], 'X').replace(chars[1], 'Y')
                    cleaned = cleaned.replace('X', 'a').replace('Y', 'b')
                elif len(chars) == 1:
                    cleaned = cleaned.replace(chars[0], 'a')'''

content = content.replace(bad_block, good_block)

with open('app/decoders/text/text_transforms.py', 'w', encoding='utf-8') as f:
    f.write(content)
