with open('app/ai/prompts/templates.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('6. Provide actionable recommendations mapped to TRON-DeCypher modules (Forensics, Binary, Memory, Network, Crypto, Decoder, Malware).', '6. Provide actionable recommendations mapped to TRON-DeCypher modules (Forensics, Binary, Memory, Network, Crypto, Decoder, Malware).\n7. The primary competition flag format is CTK{...}. Do not invent official flags.')

with open('app/ai/prompts/templates.py', 'w', encoding='utf-8') as f:
    f.write(content)
