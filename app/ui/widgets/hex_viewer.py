from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class HexViewer(QWidget):
    """A stream-capable hex viewer for large files."""
    
    def __init__(self) -> None:
        super().__init__()
        self.file_path: Path | None = None
        self.current_offset = 0
        self.page_size = 512 # Bytes per page
        
        self.init_ui()
        
    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        self.btn_prev = QPushButton("< Prev")
        self.btn_next = QPushButton("Next >")
        self.btn_prev.clicked.connect(self.page_prev)
        self.btn_next.clicked.connect(self.page_next)
        
        self.lbl_offset = QLabel("Offset: 0x0")
        self.spin_jump = QSpinBox()
        self.spin_jump.setRange(0, 999999999)
        self.spin_jump.setPrefix("0x")
        self.spin_jump.setDisplayIntegerBase(16)
        
        self.btn_jump = QPushButton("Jump")
        self.btn_jump.clicked.connect(self.jump_to_offset)
        
        ctrl_layout.addWidget(self.btn_prev)
        ctrl_layout.addWidget(self.lbl_offset)
        ctrl_layout.addWidget(self.btn_next)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(QLabel("Go to:"))
        ctrl_layout.addWidget(self.spin_jump)
        ctrl_layout.addWidget(self.btn_jump)
        
        # Viewer
        self.txt_view = QTextEdit()
        self.txt_view.setReadOnly(True)
        self.txt_view.setFont(QFont("Courier", 10))
        
        layout.addLayout(ctrl_layout)
        layout.addWidget(self.txt_view)
        
    def load_file(self, file_path: Path) -> None:
        self.file_path = file_path
        self.current_offset = 0
        
        if self.file_path and self.file_path.exists():
            self.spin_jump.setMaximum(self.file_path.stat().st_size)
            self.render_page()
            
    def render_page(self) -> None:
        if not self.file_path or not self.file_path.exists():
            return
            
        try:
            with open(self.file_path, "rb") as f:
                f.seek(self.current_offset)
                data = f.read(self.page_size)
                
            lines = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                offset_str = f"{self.current_offset + i:08X}"
                hex_str = " ".join(f"{b:02X}" for b in chunk)
                hex_str = hex_str.ljust(48) # Pad to 16 bytes
                
                ascii_str = ""
                for b in chunk:
                    if 32 <= b <= 126:
                        ascii_str += chr(b)
                    else:
                        ascii_str += "."
                        
                lines.append(f"{offset_str}  {hex_str}  |{ascii_str}|")
                
            self.txt_view.setText("\n".join(lines))
            self.lbl_offset.setText(f"Offset: 0x{self.current_offset:X}")
            
        except Exception as e:
            self.txt_view.setText(f"Error loading hex data: {e}")
            
    def page_next(self) -> None:
        if self.file_path and self.file_path.exists():
            file_size = self.file_path.stat().st_size
            if self.current_offset + self.page_size < file_size:
                self.current_offset += self.page_size
                self.render_page()
                
    def page_prev(self) -> None:
        if self.current_offset >= self.page_size:
            self.current_offset -= self.page_size
        else:
            self.current_offset = 0
        self.render_page()
        
    def jump_to_offset(self) -> None:
        self.current_offset = self.spin_jump.value()
        # Align to 16 byte boundary
        self.current_offset = self.current_offset - (self.current_offset % 16)
        self.render_page()
