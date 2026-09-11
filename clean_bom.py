import os

def clean_python_files(directory):
    for root, dirs, files in os.walk(directory):
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # If BOM is at the very beginning, keep it or remove it?
                    # The prompt says: "Do not blindly remove a legitimate UTF-8 BOM at the very beginning... The problem is specifically an embedded U+FEFF inside Python source."
                    # I will just remove ALL BOMs since Python 3 doesn't need them and it's safer.
                    # Wait, let's strictly follow the prompt: remove embedded ones.
                    
                    if b'\xef\xbb\xbf' in content:
                        # Find all occurrences
                        if content.startswith(b'\xef\xbb\xbf'):
                            # Strip first one if we want, but let's just strip everything after index 0
                            content_after_start = content[3:]
                            if b'\xef\xbb\xbf' in content_after_start:
                                content = content[:3] + content_after_start.replace(b'\xef\xbb\xbf', b'')
                                with open(file_path, 'wb') as f:
                                    f.write(content)
                                print(f"Cleaned embedded BOM from: {file_path}")
                        else:
                            content = content.replace(b'\xef\xbb\xbf', b'')
                            with open(file_path, 'wb') as f:
                                f.write(content)
                            print(f"Cleaned embedded BOM from: {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

clean_python_files('app')
clean_python_files('tests')
clean_python_files('scripts')
