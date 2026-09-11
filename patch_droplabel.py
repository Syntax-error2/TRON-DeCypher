import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add missing DropLabel class
drop_label = '''
class DropLabel(QLabel):
    file_dropped = Signal(str)
    
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa; color: #aaa; font-weight: bold; padding: 20px;")
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.file_dropped.emit(path)
                return
'''
idx = content.find("class HashRecoveryWorker(QThread):")
if idx != -1:
    content = content[:idx] + drop_label.strip('\n') + '\n\n' + content[idx:]

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
