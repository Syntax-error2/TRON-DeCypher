import os
import glob

views_dir = r"app\ui\views"
for filepath in glob.glob(os.path.join(views_dir, "*_view.py")):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "def set_case(" not in content:
        # Append a generic set_case to the class
        # We need to find the class block and append it. Simple way: just append to file.
        # However, appending to the end of the file assumes the last code block is the class.
        # Let's insert it before the end, properly indented.
        # A simple string replace is safer if we know what we are doing, but simpler:
        append_str = "\n    def set_case(self, case_id: str) -> None:\n        self.current_case_id = case_id\n"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(append_str)
        print(f"Added set_case to {filepath}")
