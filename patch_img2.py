with open('tests/qa/test_image_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('res.ocr_text.strip() if res.ocr_text else', 'res.get("ocr_text", "").strip() if res.get("ocr_text") else')
content = content.replace('if res.qr_data:', 'if res.get("qr_data"):')
content = content.replace('return res.qr_data[0]', 'return res["qr_data"][0]')
content = content.replace('if res.stego_findings:', 'if res.get("stego_findings"):')
content = content.replace('for f in res.stego_findings:', 'for f in res["stego_findings"]:')
content = content.replace('return res.stego_findings[0]', 'return res["stego_findings"][0]')

with open('tests/qa/test_image_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
