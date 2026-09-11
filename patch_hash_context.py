with open('tests/qa/test_hash_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('context_manager.active_case.custom_dictionary', 'context_manager.current_context.custom_dictionary')

with open('tests/qa/test_hash_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
