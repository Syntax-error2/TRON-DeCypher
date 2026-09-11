with open('tests/qa/test_image_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('image_analysis_service', 'image_analyzer_service')
with open('tests/qa/test_image_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
