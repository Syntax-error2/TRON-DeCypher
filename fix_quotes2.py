with open('app/ui/views/decoder_view.py', 'r', encoding='utf8') as f:
    content = f.read()

content = content.replace('html = "\n', 'html = ""\n')
# Let's fix the invalid U+2713 character issue. Wait, U+2713 is the checkmark. Python 3 supports it in strings! 
# The issue was I had ""✓ {r}<br>"" instead of "✓ {r}<br>".
# Since I replaced "" with " and "" with ", the checkmark line is now "✓ {r}<br>" which is PERFECT.
# Are there any other weird strings like "<b>HASH DETECTED</b><br><br>" that became <b>HASH DETECTED</b><br><br> ? Wait, replacing "" with " will turn html += "<b>" into html += <b>"? 
# No, if I originally wrote html += ""<b>HASH DETECTED</b><br><br>"" it would become html += "<b>HASH DETECTED</b><br><br>" which is perfect.

with open('app/ui/views/decoder_view.py', 'w', encoding='utf8') as f:
    f.write(content)
