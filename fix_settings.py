with open('app/ui/views/settings_view.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if lines[i].startswith('app_form.addRow("Version:",'):
        lines[i] = '        ' + lines[i]

with open('app/ui/views/settings_view.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
