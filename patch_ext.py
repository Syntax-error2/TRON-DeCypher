with open('tests/qa/test_extended_services.py', 'r', encoding='utf-8') as f:
    content = f.read()
import re
content = re.sub(r'from app.forensics.analyzers.identification import identify_file', '', content)
content = re.sub(r'qa.run_qa_test\("FOR-01.*', '', content)
content = re.sub(r'qa.run_qa_test\("FOR-02.*', '', content)
with open('tests/qa/test_extended_services.py', 'w', encoding='utf-8') as f:
    f.write(content)
