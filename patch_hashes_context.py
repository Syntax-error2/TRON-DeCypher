with open('tests/qa/test_hash_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

helper = '''
from app.knowledge.challenge_context import context_manager
def setup_context():
    context_manager.active_case.custom_dictionary = ["hash_recovery_test", "neon", "circuit", "defense"]
setup_context()
'''

content = content.replace('def run_hash_generator(', helper + '\ndef run_hash_generator(')

with open('tests/qa/test_hash_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
