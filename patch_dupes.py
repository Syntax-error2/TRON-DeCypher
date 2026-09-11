import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I accidentally duplicated inline_browse_wordlist, inline_start_recovery, inline_cancel_recovery when patching.
# Let's fix this by deleting the old versions.

# We know the new versions are right after 	oggle_advanced(self) and before the end of the file.
# The old ones were after inline_browse_wordlist(self)

patch_regex = r"    def inline_browse_wordlist\(self\) -> None:\n(?:.*\n)*?    def inline_start_recovery\(self\) -> None:\n(?:.*\n)*?    def inline_cancel_recovery\(self\) -> None:\n(?:.*\n)*?(?=class)"

content = re.sub(patch_regex, "", content)

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
