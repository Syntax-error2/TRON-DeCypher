import sys

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication

from app.decoders.core.registry import decoder_registry
from app.decoders.encoding.base64_decoder import Base64Decoder
from app.ui.views.decoder_view import DecoderView


def test_decoder_detection_link_passes_context() -> None:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    decoder_registry.register(Base64Decoder())
    
    view = DecoderView()
    view.current_case_id = "test_case_123"
    view.txt_input.setPlainText("SGVsbG8gV29ybGQh") # Base64 for "Hello World!"
    
    url = QUrl("enc:base64")
    view.on_detection_link_clicked(url)
    
    assert "Hello World!" in view.txt_output.toPlainText()
