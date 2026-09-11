with open('tests/qa/test_image_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('image_analyzer_service.analyze(path, [\'ocr\'])', 'image_analyzer_service.analyze(path)')
content = content.replace('image_analyzer_service.analyze(path, [\'qr\'])', 'image_analyzer_service.analyze(path)')
content = content.replace('image_analyzer_service.analyze(path, [\'stego\'])', 'image_analyzer_service.analyze(path)')

with open('tests/qa/test_image_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
