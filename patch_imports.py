import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# find local import and delete it
content = content.replace("from PySide6.QtWidgets import QCheckBox, QSpinBox, QComboBox, QFormLayout", "")

# add to global imports
global_import = '''
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
'''
# Replace the current PySide6.QtWidgets import block
content = re.sub(r'from PySide6\.QtWidgets import \([\s\S]*?\)', global_import.strip('\n'), content)

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
