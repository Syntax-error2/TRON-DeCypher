with open('tests/qa/test_hash_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

helper = '''
def run_hash_generator(target, algo, cfg):
    for step in hash_recovery_service.recover_automatic_generator(target, algo, cfg):
        if step.get('status') == 'MATCH':
            return step.get('candidate')
    return None
'''

content = content.replace('def get_hash(', helper + '\ndef get_hash(')

# Replace the lambda expressions for hash recovery
import re
content = re.sub(
    r'lambda x, a=algo: hash_recovery_service.recover_automatic_generator\(x, a, (cfg.*?)\)\.candidate',
    r'lambda x, a=algo: run_hash_generator(x, a, \1)',
    content
)
content = re.sub(
    r'lambda x: hash_recovery_service.recover_automatic_generator\(x, "md5", (cfg.*?)\)\.candidate',
    r'lambda x: run_hash_generator(x, "md5", \1)',
    content
)

with open('tests/qa/test_hash_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
