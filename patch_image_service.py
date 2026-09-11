with open('tests/qa/test_image_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('app.services.image_analysis', 'app.services.image_analyzer')

with open('tests/qa/test_image_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
