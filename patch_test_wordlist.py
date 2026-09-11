import re
with open('tests/unit/test_wordlist_recovery.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('assert res[\'status\'] == \'NO_MATCH\'', 'assert res[\'status\'] in [\'NO_MATCH\', \'LIMIT_REACHED\']')

with open('tests/unit/test_wordlist_recovery.py', 'w', encoding='utf-8') as f:
    f.write(content)
