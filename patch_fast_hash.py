with open('tests/qa/test_hash_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

helper = '''
def setup_context():
    context_manager.current_context.custom_dictionary = ["hash_recovery_test", "neon", "circuit", "defense"]
    # Mock the master wordlist so it's super fast
    from app.knowledge.registry import knowledge_registry
    knowledge_registry.get_master_wordlist = lambda: []
'''

content = content.replace('''def setup_context():
    context_manager.current_context.custom_dictionary = ["hash_recovery_test", "neon", "circuit", "defense"]''', helper)

with open('tests/qa/test_hash_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
