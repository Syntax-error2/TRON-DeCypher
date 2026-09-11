with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(r'res_str += f"\nFLAG CANDIDATE: {flags[0]}"', r'res_str += f"\n🚩 CTK FLAG CANDIDATE: {flags[0]}"')
content = content.replace('marker = " \ud83d\udea9 FLAG CANDIDATE"', 'marker = " 🚩 CTK FLAG CANDIDATE"')

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
