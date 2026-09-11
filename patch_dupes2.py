import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I am just going to split the string manually at the old inline_browse_wordlist 
# and delete everything until the new inline_browse_wordlist.

parts = content.split("    def inline_browse_wordlist(self) -> None:")
if len(parts) >= 3:
    # There are two implementations. We want to keep everything before the first one,
    # and everything from the second one onwards.
    content = parts[0] + "    def inline_browse_wordlist(self) -> None:" + parts[2]
    
with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
