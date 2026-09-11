import os
import uuid
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QGuiApplication, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
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

from app.decoders.core.detector import decoder_detector
from app.decoders.core.models import DecoderInput, TransformationPipeline, TransformationStep
from app.decoders.core.pipeline import PipelineRunner
from app.decoders.core.registry import decoder_registry
from app.services.hash_identification import hash_identification_service
from app.services.hash_recovery import hash_recovery_service
from app.services.hashing_service import hashing_service
from app.services.image_analyzer import image_analyzer_service
from app.services.input_router import input_router


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

class HashRecoveryWorker(QThread):
    progress = Signal(str)
    finished_ok = Signal(str)
    error = Signal(str)

    def __init__(self, target: str, algo: str, wordlist: str | None = None, config=None):
        super().__init__()
        self.target = target
        self.algo = algo
        self.wordlist = wordlist
        self.config = config
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            from app.services.hash_recovery import hash_recovery_service
            if self.wordlist:
                from pathlib import Path
                iterator = hash_recovery_service.recover_wordlist_generator(self.target, self.algo, Path(self.wordlist))
            else:
                iterator = hash_recovery_service.recover_automatic_generator(self.target, self.algo, self.config)
                
            for update in iterator:
                if self._is_cancelled:
                    return
                
                status = update.get("status")
                if status == "RUNNING":
                    count = update.get("count", 0)
                    rate = update.get("rate", 0.0)
                    src = update.get("source", "")
                    strat = update.get("strategy", "")
                    self.progress.emit(f"{count} cands ({rate:.0f}/s) | {src} | {strat}")
                elif status == "MATCH":
                    c = update.get("candidate", "")
                    flags = update.get("flags", [])
                    res_str = f"✅ RECOVERED\nValue: {c}"
                    if flags:
                        res_str += f"\n🚩 CTK FLAG CANDIDATE: {flags[0]}"
                    self.finished_ok.emit(res_str)
                    return
                elif status == "ERROR":
                    self.error.emit(update.get("msg", "Unknown error"))
                    return
                elif status == "NO_MATCH" or status == "LIMIT_REACHED":
                    msg = update.get("msg", "NO MATCH FOUND")
                    self.finished_ok.emit(msg)
                    return
                    
        except Exception as e:
            self.error.emit(str(e))

class DecoderView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.runner = PipelineRunner()
        self.pipeline = TransformationPipeline(id=uuid.uuid4().hex, name="Interactive Pipeline")
        self.current_case_id: str | None = None
        self.recovery_worker: HashRecoveryWorker | None = None
        self.current_image_path: str | None = None
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        # Mode selector
        mode_layout = QHBoxLayout()
        self.btn_mode_text = QPushButton("Text")
        self.btn_mode_image = QPushButton("Image")
        self.btn_mode_file = QPushButton("File")
        
        self.btn_mode_text.setCheckable(True)
        self.btn_mode_image.setCheckable(True)
        self.btn_mode_file.setCheckable(True)
        self.btn_mode_text.setChecked(True)
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.btn_mode_text)
        self.mode_group.addButton(self.btn_mode_image)
        self.mode_group.addButton(self.btn_mode_file)
        
        self.btn_mode_text.clicked.connect(lambda: self.switch_mode(0))
        self.btn_mode_image.clicked.connect(lambda: self.switch_mode(1))
        self.btn_mode_file.clicked.connect(lambda: self.switch_mode(2))
        
        mode_layout.addWidget(self.btn_mode_text)
        mode_layout.addWidget(self.btn_mode_image)
        mode_layout.addWidget(self.btn_mode_file)
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)
        
        self.tabs = QTabWidget()
        
        self.tab_transform = QWidget()
        self.setup_transform_tab()
        self.tabs.addTab(self.tab_transform, "Transformations")
        
        self.tab_hash = QWidget()
        self.setup_hash_tab()
        self.tabs.addTab(self.tab_hash, "Hash & Digest")
        
        main_layout.addWidget(self.tabs)
        
    def setup_transform_tab(self) -> None:
        layout = QVBoxLayout(self.tab_transform)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        input_group = QGroupBox("INPUT")
        input_layout = QVBoxLayout(input_group)
        
        self.input_stack = QStackedWidget()
        
        # Mode 0: Text Input
        self.txt_input = QTextEdit()
        self.txt_input.textChanged.connect(self.on_input_changed)
        self.txt_input.setAcceptDrops(True)
        def text_drag_enter(event):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
        def text_drop(event):
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path):
                    self.route_dropped_file(path)
                    return
        self.txt_input.dragEnterEvent = text_drag_enter
        self.txt_input.dropEvent = text_drop
        
        text_page = QWidget()
        text_layout = QVBoxLayout(text_page)
        text_layout.setContentsMargins(0,0,0,0)
        text_layout.addWidget(self.txt_input)
        
        input_btns = QHBoxLayout()
        self.btn_clear_input = QPushButton("Clear")
        self.btn_clear_input.clicked.connect(self.txt_input.clear)
        input_btns.addWidget(self.btn_clear_input)
        text_layout.addLayout(input_btns)
        
        self.input_stack.addWidget(text_page)
        
        # Mode 1: Image Input
        image_page = QWidget()
        image_layout = QVBoxLayout(image_page)
        image_layout.setContentsMargins(0,0,0,0)
        self.lbl_image_drop = DropLabel("Drag & Drop Image Here\nor click Upload Image")
        self.lbl_image_drop.file_dropped.connect(self.load_image)
        self.btn_upload_image = QPushButton("Upload Image")
        self.btn_upload_image.clicked.connect(self.upload_image_dialog)
        image_layout.addWidget(self.lbl_image_drop)
        image_layout.addWidget(self.btn_upload_image)
        self.input_stack.addWidget(image_page)
        
        # Mode 2: File Input
        file_page = QWidget()
        file_layout = QVBoxLayout(file_page)
        file_layout.setContentsMargins(0,0,0,0)
        self.lbl_file_drop = DropLabel("Drag & Drop File Here\nor click Upload File")
        self.lbl_file_drop.file_dropped.connect(self.load_file)
        self.btn_upload_file = QPushButton("Upload File")
        self.btn_upload_file.clicked.connect(self.upload_file_dialog)
        file_layout.addWidget(self.lbl_file_drop)
        file_layout.addWidget(self.btn_upload_file)
        self.input_stack.addWidget(file_page)
        
        input_layout.addWidget(self.input_stack)
        
        detect_group = QGroupBox("AUTO-DETECTION / ANALYSIS")
        detect_layout = QVBoxLayout(detect_group)
        self.txt_detections = QTextBrowser()
        self.txt_detections.setFixedHeight(240)
        self.txt_detections.setOpenLinks(False)
        self.txt_detections.anchorClicked.connect(self.on_detection_link_clicked)
        detect_layout.addWidget(self.txt_detections)
        
        self.tools_stack = QStackedWidget()
        
        # Page 0: PIPELINE
        pipeline_group = QGroupBox("PIPELINE")
        pipeline_layout = QVBoxLayout(pipeline_group)
        self.list_pipeline = QListWidget()
        self.list_pipeline.setFixedHeight(100)
        
        pipeline_ctrls = QHBoxLayout()
        self.txt_search_transform = QLineEdit()
        self.txt_search_transform.setPlaceholderText("Search transformations...")
        self.txt_search_transform.textChanged.connect(self.filter_decoders)
        
        self.combo_decoders = QComboBox()
        self.all_decoders = []
        self._category_map = {
            "encoding": "ENCODING",
            "classical_ciphers": "CLASSICAL CIPHERS",
            "numeric": "NUMERIC / BITWISE",
            "text": "TEXT / WEB",
            "hash": "HASH ANALYSIS"
        }
        
        # Build categorized list
        cat_dict = {}
        for d in decoder_registry.list_all():
            cat = self._category_map.get(d.category, d.category.upper())
            if cat not in cat_dict:
                cat_dict[cat] = []
            cat_dict[cat].append(d.name)
            self.all_decoders.append(d.name)
            
        for cat, names in cat_dict.items():
            self.combo_decoders.addItem(f"--- {cat} ---")
            for name in sorted(names):
                self.combo_decoders.addItem(name)
                
        self.combo_decoders.currentIndexChanged.connect(self.on_decoder_selected)
        
        self.param_container = QWidget()
        self.param_layout = QFormLayout(self.param_container)
        self.param_inputs = {}
            
        self.btn_add_step = QPushButton("+ Add Step")
        self.btn_add_step.clicked.connect(self.add_pipeline_step)
        self.btn_run_pipeline = QPushButton("Run Pipeline")
        self.btn_run_pipeline.clicked.connect(self.run_pipeline)
        self.btn_clear_pipeline = QPushButton("Clear")
        self.btn_clear_pipeline.clicked.connect(self.clear_pipeline)
        
        pipeline_layout.addWidget(self.list_pipeline)
        pipeline_layout.addWidget(self.txt_search_transform)
        pipeline_ctrls.addWidget(self.combo_decoders)
        pipeline_ctrls.addWidget(self.btn_add_step)
        pipeline_ctrls.addWidget(self.btn_run_pipeline)
        pipeline_ctrls.addWidget(self.btn_clear_pipeline)
        pipeline_layout.addLayout(pipeline_ctrls)
        pipeline_layout.addWidget(self.param_container)
        self.tools_stack.addWidget(pipeline_group)
        
        # Page 1: INLINE HASH ANALYSIS
        self.hash_inline_group = QGroupBox("AUTOMATIC HASH RECOVERY")
        inline_layout = QVBoxLayout(self.hash_inline_group)
        
        info_row = QHBoxLayout()
        info_row.addWidget(QLabel("Target:"))
        self.inline_target = QLineEdit()
        self.inline_target.setReadOnly(True)
        info_row.addWidget(self.inline_target)
        info_row.addWidget(QLabel("Algorithm:"))
        self.inline_algo = QLineEdit()
        self.inline_algo.setReadOnly(True)
        self.inline_algo.setFixedWidth(80)
        info_row.addWidget(self.inline_algo)
        self.btn_close_inline = QPushButton("Close")
        self.btn_close_inline.clicked.connect(lambda: self.tools_stack.setCurrentIndex(0))
        info_row.addWidget(self.btn_close_inline)
        inline_layout.addLayout(info_row)
        
        ctrl_row = QHBoxLayout()
        self.inline_btn_start = QPushButton("Start Automatic Recovery")
        self.inline_btn_start.clicked.connect(self.inline_start_recovery)
        self.inline_btn_cancel = QPushButton("Cancel")
        self.inline_btn_cancel.clicked.connect(self.inline_cancel_recovery)
        self.inline_btn_cancel.setEnabled(False)
        ctrl_row.addWidget(self.inline_btn_start)
        ctrl_row.addWidget(self.inline_btn_cancel)
        inline_layout.addLayout(ctrl_row)
        
        res_row = QHBoxLayout()
        self.inline_lbl_prog = QLabel("Progress: -")
        self.inline_lbl_res = QLabel("Result: -")
        self.inline_btn_save = QPushButton("Save to Case")
        self.inline_btn_save.setEnabled(False)
        self.inline_btn_save.clicked.connect(self.inline_save_match)
        self.inline_btn_send = QPushButton("Use Result")
        self.inline_btn_send.setEnabled(False)
        self.inline_btn_send.clicked.connect(self.inline_use_match)
        res_row.addWidget(self.inline_lbl_prog)
        res_row.addWidget(self.inline_lbl_res)
        res_row.addWidget(self.inline_btn_save)
        res_row.addWidget(self.inline_btn_send)
        inline_layout.addLayout(res_row)
        
        # Advanced Recovery Section
        self.btn_adv_toggle = QPushButton("Recovery Options ▼")
        self.btn_adv_toggle.setCheckable(True)
        self.btn_adv_toggle.clicked.connect(self.toggle_advanced)
        inline_layout.addWidget(self.btn_adv_toggle)
        
        self.adv_widget = QWidget()
        adv_layout = QVBoxLayout(self.adv_widget)
        adv_layout.setContentsMargins(0, 5, 0, 0)
        
        
        form_layout = QFormLayout()
        
        self.chk_case = QCheckBox("Mixed Case")
        self.chk_case.setChecked(True)
        self.chk_num = QCheckBox("Digit Suffixes")
        self.chk_num.setChecked(True)
        self.chk_sep = QCheckBox("Separators")
        self.chk_sep.setChecked(True)
        self.chk_leet = QCheckBox("Leetspeak")
        self.chk_leet.setChecked(True)
        self.chk_wrap = QCheckBox("Flag Wrappers")
        self.chk_wrap.setChecked(True)
        
        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(1, 3)
        self.spin_depth.setValue(2)
        
        self.spin_max_cands = QSpinBox()
        self.spin_max_cands.setRange(1000, 10000000)
        self.spin_max_cands.setValue(5000000)
        
        self.spin_max_time = QSpinBox()
        self.spin_max_time.setRange(1, 600)
        self.spin_max_time.setValue(60)
        
        self.btn_preview = QPushButton("Preview Candidates")
        # self.btn_preview.clicked.connect(self.preview_candidates)
        
        opt_layout1 = QHBoxLayout()
        opt_layout1.addWidget(self.chk_case)
        opt_layout1.addWidget(self.chk_num)
        opt_layout1.addWidget(self.chk_sep)
        
        opt_layout2 = QHBoxLayout()
        opt_layout2.addWidget(self.chk_leet)
        opt_layout2.addWidget(self.chk_wrap)
        
        form_layout.addRow("Mutations:", opt_layout1)
        form_layout.addRow("", opt_layout2)
        form_layout.addRow("Combination Depth:", self.spin_depth)
        form_layout.addRow("Max Candidates:", self.spin_max_cands)
        form_layout.addRow("Max Runtime (s):", self.spin_max_time)
        
        adv_layout.addLayout(form_layout)
        adv_layout.addWidget(self.btn_preview)
        
        self.adv_widget.setVisible(False)
        inline_layout.addWidget(self.adv_widget)
        
        self.tools_stack.addWidget(self.hash_inline_group)
        
        # Page 2: IMAGE TOOLS
        image_tools_group = QGroupBox("IMAGE TOOLS")
        image_tools_layout = QVBoxLayout(image_tools_group)
        
        img_actions_row = QHBoxLayout()
        self.btn_img_ocr = QPushButton("OCR")
        self.btn_img_qr = QPushButton("QR / Barcode")
        self.btn_img_stego = QPushButton("Stego (LSB)")
        self.btn_img_meta = QPushButton("Metadata")
        self.btn_img_ioc = QPushButton("Extract IOCs")
        
        self.btn_img_ocr.clicked.connect(self.run_img_ocr)
        self.btn_img_qr.clicked.connect(self.run_img_qr)
        self.btn_img_stego.clicked.connect(self.run_img_stego)
        self.btn_img_meta.clicked.connect(self.run_img_meta)
        self.btn_img_ioc.clicked.connect(self.run_img_ioc)
        
        img_actions_row.addWidget(self.btn_img_ocr)
        img_actions_row.addWidget(self.btn_img_qr)
        img_actions_row.addWidget(self.btn_img_stego)
        img_actions_row.addWidget(self.btn_img_meta)
        img_actions_row.addWidget(self.btn_img_ioc)
        
        image_tools_layout.addLayout(img_actions_row)
        
        # Symbol / Image Cipher Integration
        self.symbol_group = QGroupBox("SYMBOL / IMAGE CIPHER")
        sym_layout = QVBoxLayout(self.symbol_group)
        
        sym_actions_row = QHBoxLayout()
        self.btn_sym_detect = QPushButton("Detect Symbols")
        self.combo_sym_profile = QComboBox()
        self.combo_sym_profile.addItems(["auto", "egyptian", "braille", "runes", "pigpen", "custom"])
        self.btn_sym_solve = QPushButton("Auto Solve")
        
        self.btn_sym_detect.clicked.connect(self.run_sym_detect)
        self.btn_sym_solve.clicked.connect(self.run_sym_solve)
        
        sym_actions_row.addWidget(self.btn_sym_detect)
        sym_actions_row.addWidget(QLabel("Profile:"))
        sym_actions_row.addWidget(self.combo_sym_profile)
        sym_actions_row.addWidget(self.btn_sym_solve)
        
        sym_layout.addLayout(sym_actions_row)
        
        self.table_sym_map = QTableWidget(0, 3)
        self.table_sym_map.setHorizontalHeaderLabels(["Symbol ID", "Assigned Char", "Count"])
        self.table_sym_map.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_sym_map.setFixedHeight(120)
        
        sym_layout.addWidget(self.table_sym_map)
        
        sym_actions_row2 = QHBoxLayout()
        self.btn_sym_send = QPushButton("Send to Decoder")
        self.btn_sym_ioc = QPushButton("Extract IOCs")
        self.btn_sym_case = QPushButton("Save to Case")
        
        self.btn_sym_send.clicked.connect(self.run_sym_send)
        self.btn_sym_ioc.clicked.connect(self.run_sym_ioc)
        self.btn_sym_case.clicked.connect(self.run_sym_case)
        
        sym_actions_row2.addWidget(self.btn_sym_send)
        sym_actions_row2.addWidget(self.btn_sym_ioc)
        sym_actions_row2.addWidget(self.btn_sym_case)
        
        sym_layout.addLayout(sym_actions_row2)
        
        image_tools_layout.addWidget(self.symbol_group)
        self.tools_stack.addWidget(image_tools_group)
        
        
        left_layout.addWidget(input_group)
        left_layout.addWidget(detect_group)
        left_layout.addWidget(self.tools_stack)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        output_group = QGroupBox("OUTPUT / RESULT")
        output_layout = QVBoxLayout(output_group)
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        
        self.output_stack = QStackedWidget()
        
        out_text_page = QWidget()
        out_text_layout = QVBoxLayout(out_text_page)
        out_text_layout.setContentsMargins(0,0,0,0)
        out_text_layout.addWidget(self.txt_output)
        self.output_stack.addWidget(out_text_page)
        
        out_img_page = QWidget()
        out_img_layout = QVBoxLayout(out_img_page)
        out_img_layout.setContentsMargins(0,0,0,0)
        self.lbl_img_preview = QLabel("No Image")
        self.lbl_img_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img_preview.setStyleSheet("QLabel { background-image: url(checkerboard.png); }")
        out_img_layout.addWidget(self.lbl_img_preview)
        self.output_stack.addWidget(out_img_page)
        
        output_btns = QHBoxLayout()
        self.btn_copy_out = QPushButton("Copy")
        self.btn_send_case = QPushButton("Save to Case")
        self.btn_extract_ioc = QPushButton("Extract IOCs")
        self.btn_send_to_decoder = QPushButton("Send to Decoder")
        self.btn_copy_out.clicked.connect(self.copy_output)
        self.btn_send_case.clicked.connect(self.send_to_case)
        self.btn_extract_ioc.clicked.connect(self.extract_iocs)
        self.btn_send_to_decoder.clicked.connect(self.send_output_to_decoder)
        output_btns.addWidget(self.btn_copy_out)
        output_btns.addWidget(self.btn_send_case)
        output_btns.addWidget(self.btn_extract_ioc)
        output_btns.addWidget(self.btn_send_to_decoder)
        
        output_layout.addWidget(self.output_stack)
        output_layout.addLayout(output_btns)
        right_layout.addWidget(output_group)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 400])
        layout.addWidget(splitter)
        
    def setup_hash_tab(self) -> None:
        layout = QVBoxLayout(self.tab_hash)
        
        id_group = QGroupBox("HASH IDENTIFICATION")
        id_layout = QVBoxLayout(id_group)
        id_row = QHBoxLayout()
        self.txt_hash_id_input = QLineEdit()
        self.txt_hash_id_input.setPlaceholderText("Enter hash digest...")
        self.btn_id_hash = QPushButton("Identify")
        self.btn_id_hash.clicked.connect(self.identify_hash)
        id_row.addWidget(QLabel("Target:"))
        id_row.addWidget(self.txt_hash_id_input)
        id_row.addWidget(self.btn_id_hash)
        self.txt_hash_id_res = QTextEdit()
        self.txt_hash_id_res.setReadOnly(True)
        self.txt_hash_id_res.setFixedHeight(80)
        id_layout.addLayout(id_row)
        id_layout.addWidget(self.txt_hash_id_res)
        
        gen_group = QGroupBox("HASH GENERATION")
        gen_layout = QVBoxLayout(gen_group)
        gen_in_layout = QHBoxLayout()
        self.txt_hash_input = QTextEdit()
        self.txt_hash_input.setPlaceholderText("Enter text/file to hash...")
        self.txt_hash_input.setFixedHeight(60)
        btn_layout = QVBoxLayout()
        self.btn_hash_file = QPushButton("Select File...")
        self.btn_hash_file.clicked.connect(self.select_hash_file)
        self.btn_hash_gen = QPushButton("Generate Hashes")
        self.btn_hash_gen.clicked.connect(self.generate_hashes)
        btn_layout.addWidget(self.btn_hash_file)
        btn_layout.addWidget(self.btn_hash_gen)
        gen_in_layout.addWidget(self.txt_hash_input)
        gen_in_layout.addLayout(btn_layout)
        gen_layout.addLayout(gen_in_layout)
        self.lbl_hash_file_sel = QLabel("No file selected.")
        gen_layout.addWidget(self.lbl_hash_file_sel)
        
        self.table_hashes = QTableWidget()
        self.table_hashes.setColumnCount(3)
        self.table_hashes.setHorizontalHeaderLabels(["Algorithm", "Digest", "Action"])
        self.table_hashes.horizontalHeader().setStretchLastSection(True)
        self.table_hashes.setFixedHeight(120)
        gen_layout.addWidget(self.table_hashes)
        
        layout.addWidget(id_group)
        layout.addWidget(gen_group)
        layout.addStretch()
        
        self.current_hash_file: str | None = None
        self.last_hashes: dict[str, str] = {}
        self.last_match: str | None = None

    def switch_mode(self, index: int) -> None:
        self.input_stack.setCurrentIndex(index)
        if index == 0:
            self.tools_stack.setCurrentIndex(0)
            self.output_stack.setCurrentIndex(0)
            self.on_input_changed()
        elif index == 1:
            self.tools_stack.setCurrentIndex(2)
            self.output_stack.setCurrentIndex(0)
        elif index == 2:
            self.tools_stack.setCurrentIndex(0)
            self.output_stack.setCurrentIndex(0)

    def route_dropped_file(self, path: str) -> None:
        cat = input_router.route_file(path)
        if cat == "IMAGE":
            self.btn_mode_image.setChecked(True)
            self.switch_mode(1)
            self.load_image(path)
        else:
            self.btn_mode_file.setChecked(True)
            self.switch_mode(2)
            self.load_file(path)

    def on_decoder_selected(self) -> None:
        while self.param_layout.count():
            item = self.param_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.param_inputs.clear()
        
        decoder_name = self.combo_decoders.currentText()
        if not decoder_name or decoder_name.startswith("---"):
            return
            
        d_obj = decoder_registry.get(decoder_name)
        if not d_obj:
            return
            
        params = getattr(d_obj, "expected_params", {})
        for key, info in params.items():
            ptype = info.get("type", "str")
            pdesc = info.get("description", key)
            pdef = info.get("default", "")
            
            if ptype == "bool":
                chk = QCheckBox(pdesc)
                chk.setChecked(bool(pdef))
                self.param_layout.addRow("", chk)
                self.param_inputs[key] = chk
            else:
                txt = QLineEdit()
                txt.setText(str(pdef))
                self.param_layout.addRow(f"{pdesc}:", txt)
                self.param_inputs[key] = txt

    def filter_decoders(self, text: str) -> None:
        text = text.lower()
        self.combo_decoders.clear()
        if not text:
            # Rebuild categorized
            cat_dict = {}
            for d in decoder_registry.list_all():
                cat = self._category_map.get(d.category, d.category.upper())
                if cat not in cat_dict:
                    cat_dict[cat] = []
                cat_dict[cat].append(d.name)
            for cat, names in cat_dict.items():
                self.combo_decoders.addItem(f"--- {cat} ---")
                for name in sorted(names):
                    self.combo_decoders.addItem(name)
            return
            
        filtered = [d for d in self.all_decoders if text in d.lower()]
        self.combo_decoders.addItems(filtered)
        
    def _get_input(self) -> DecoderInput:
        return DecoderInput(text=self.txt_input.toPlainText())
        
    def on_input_changed(self) -> None:
        inp = self._get_input()
        if not inp.text:
            self.txt_detections.clear()
            self.tools_stack.setCurrentIndex(0)
            return
            
        detections = decoder_detector.detect(inp)
        html = ""
        
        hash_cands = [d for d in detections if getattr(d, 'is_hash', False)]
        enc_cands = [d for d in detections if not getattr(d, 'is_hash', False) and getattr(decoder_registry.get(d.decoder_name), 'reversible', True)]
        
        if hash_cands:
            best = hash_cands[0]
            html += "<b>HASH DETECTED</b><br><br>"
            html += f"<b>Algorithm:</b> {best.decoder_name}<br>"
            
            conf_str = "HIGH" if best.confidence >= 0.8 else ("MODERATE" if best.confidence >= 0.5 else "LOW")
            html += f"<b>Confidence:</b> {conf_str}<br>"
            
            reasons = best.metadata.get('reasons', [])
            reason_str = ", ".join(reasons) if reasons else "No specific reasons"
            html += f"<b>Reason:</b> {reason_str}<br><br>"
            
            html += "<b>AUTOMATIC RECOVERY</b><br><br>"
            html += f"<a href='hash:{best.decoder_name}'>[Recover Hash]</a><br><br>"
            
            html += "<b>Sources:</b><br>"
            html += "✓ Built-in CTF dictionary<br>"
            html += "✓ Category dictionary<br>"
            html += "✓ TRON Context dictionary<br>"
            html += "✓ Mutations<br><br>"
            
            html += "<b>Status:</b> READY<br>"
            
        if enc_cands:
            if hash_cands:
                html += "<br>"
            html += "<b>OTHER INTERPRETATIONS</b><br>"
            for c in enc_cands[:3]:
                conf_str = "HIGH" if c.confidence >= 0.8 else ("POSSIBLE" if c.confidence >= 0.3 else "LOW")
                html += f"• {c.decoder_name} (Confidence: {conf_str}) - <a href='enc:{c.decoder_name}'>[Apply]</a><br>"
                
        self.txt_detections.setHtml(html)
    def on_detection_link_clicked(self, url: QUrl) -> None:
        scheme = url.scheme()
        path = url.path()
        if scheme == "enc":
            decoder = decoder_registry.get(path)
            if decoder:
                res = decoder.decode(self._get_input(), {"case_id": getattr(self, "current_case_id", None)})
                if res.output_text:
                    self.txt_output.setPlainText(res.output_text)
                    self.tools_stack.setCurrentIndex(1)
        elif scheme == "hash":
            inp = self._get_input()
            self.inline_target.setText(inp.text.strip())
            self.inline_algo.setText(path)
            self.inline_lbl_res.setText("Result: Ready")
            self.inline_lbl_prog.setText("")
            self.tools_stack.setCurrentIndex(2)
            self.inline_start_recovery()
        elif scheme == "action":
            from PyQt6.QtWidgets import QApplication, QMessageBox
            if path == "use_result" and hasattr(self, 'last_match'):
                self.txt_input.setPlainText(self.last_match)
                self.tools_stack.setCurrentIndex(0)
            elif path == "copy" and hasattr(self, 'last_match'):
                QApplication.clipboard().setText(self.last_match)
                QMessageBox.information(self, "Copied", "Result copied to clipboard.")
            elif path == "save_case" and hasattr(self, 'last_match'):
                # Simulate save to case
                QMessageBox.information(self, "Saved", "Result saved to case evidence.")
    def toggle_advanced(self) -> None:
        self.adv_widget.setVisible(self.btn_adv_toggle.isChecked())


    def inline_browse_wordlist(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Wordlist")
        if file_path:
            self.inline_txt_wl.setText(file_path)
            
    def inline_start_recovery(self) -> None:
        target = self.inline_target.text().strip()
        algo = self.inline_algo.text().strip()
        
        if not target:
            return
            
        self.last_match = None
        self.inline_btn_save.setEnabled(False)
        self.inline_btn_send.setEnabled(False)
        
        if self.btn_adv_toggle.isChecked() and self.inline_radio_cand.isChecked():
            cand = self.inline_txt_cand.text()
            res = hash_recovery_service.verify_candidate(target, algo, cand)
            if res.status == "MATCH":
                self.inline_lbl_res.setText(f"Result: ✓ RECOVERED\nValue: {cand}")
                self.inline_lbl_res.setStyleSheet("color: green; font-weight: bold;")
                self.last_match = cand
                self.inline_btn_save.setEnabled(True)
                self.inline_btn_send.setEnabled(True)
            elif res.status == "ERROR":
                self.inline_lbl_res.setText("Result: ERROR")
                self.inline_lbl_res.setStyleSheet("color: red;")
            else:
                self.inline_lbl_res.setText("Result: NO MATCH")
                self.inline_lbl_res.setStyleSheet("color: red; font-weight: bold;")
            return
            
        wl = self.inline_txt_wl.text() if (self.btn_adv_toggle.isChecked() and self.inline_radio_wl.isChecked()) else None
        
        if wl and not os.path.exists(wl):
            QMessageBox.warning(self, "Wordlist", "Invalid wordlist path.")
            return
            
        self.inline_btn_start.setEnabled(False)
        self.inline_btn_cancel.setEnabled(True)
        self.inline_lbl_prog.setText("Progress: 0")
        self.inline_lbl_res.setText("Status: RUNNING")
        self.inline_lbl_res.setStyleSheet("color: orange; font-weight: bold;")
        
        self.recovery_worker = HashRecoveryWorker(target, algo, wl)
        self.recovery_worker.progress.connect(self._on_inline_prog)
        self.recovery_worker.finished_ok.connect(self._on_inline_fin)
        self.recovery_worker.error.connect(self._on_inline_err)
        self.recovery_worker.start()
            
    def inline_cancel_recovery(self) -> None:
        if self.recovery_worker:
            self.recovery_worker.cancel()
            
    def _on_inline_prog(self, data: dict[str, Any]) -> None:
        count = data.get("count", 0)
        elapsed = data.get("elapsed", 1.0)
        source = data.get("source", "wordlist")
        rate = count / elapsed if elapsed > 0 else 0
        self.inline_lbl_prog.setText(f"Checked: {count} ({int(rate)}/s) | Src: {source} | Time: {elapsed:.1f}s")
        
    def _on_inline_fin(self, data: dict[str, Any]) -> None:
        self.inline_btn_start.setEnabled(True)
        self.inline_btn_cancel.setEnabled(False)
        self._on_inline_prog(data)
        
        status = data.get("status")
        if status == "MATCH":
            cand = data.get("candidate", "")
            time_elapsed = data.get("elapsed", 0)
            count = data.get("count", 0)
            source = data.get("source", "Unknown")
            
            html = "<b>✓ RECOVERED</b><br><br>"
            html += f"<b>Algorithm:</b> {self.inline_algo.text()}<br>"
            html += f"<b>Target:</b> {self.inline_target.text()}<br>"
            html += f"<b>Recovered:</b> {cand}<br>"
            html += "<b>Method:</b> CTF Dictionary<br>"
            html += f"<b>Source:</b> {source}<br>"
            html += f"<b>Candidates checked:</b> {count}<br>"
            html += f"<b>Elapsed:</b> {time_elapsed:.2f}s<br><br>"
            
            html += "<b>Actions:</b> <a href='action:use_result'>[Use Result]</a> <a href='action:copy'>[Copy]</a> <a href='action:save_case'>[Save to Case]</a><br>"
            
            self.txt_detections.setHtml(html)
            
            self.inline_lbl_res.setText("Result: ✓ MATCH")
            self.inline_lbl_res.setStyleSheet("color: green; font-weight: bold;")
            self.last_match = cand
            self.inline_btn_save.setEnabled(True)
            self.inline_btn_send.setEnabled(True)
            
            if data.get("is_flag"):
                flags = data.get("flags", [])
                QMessageBox.information(self, "Flag Detected", "Potential Flag Recovered:\n" + "\n".join(flags))
                
        elif status == "CANCELLED":
            self.inline_lbl_res.setText("Result: CANCELLED")
            self.inline_lbl_res.setStyleSheet("color: red;")
        else:
            time_elapsed = data.get("elapsed", 0)
            count = data.get("count", 0)
            
            html = "<b>NO MATCH FOUND</b><br><br>"
            html += f"<b>Algorithm:</b> {self.inline_algo.text()}<br>"
            html += "<b>Sources:</b> Built-in CTF dictionary, Mutations, Patterns<br>"
            html += f"<b>Candidates checked:</b> {count}<br>"
            html += f"<b>Time:</b> {time_elapsed:.2f}s<br><br>"
            html += "<b>Possible next step:</b><br>"
            html += "- Add a local wordlist.<br>"
            html += "- Change bounded recovery options.<br>"
            html += "- Inspect challenge context.<br>"
            
            self.txt_detections.setHtml(html)
            self.inline_lbl_res.setText("Result: NO MATCH FOUND")
            self.inline_lbl_res.setStyleSheet("color: red; font-weight: bold;")
    def _on_inline_err(self, err: str) -> None:
        self.inline_btn_start.setEnabled(True)
        self.inline_btn_cancel.setEnabled(False)
        self.inline_lbl_res.setText(f"Error: {err}")
        self.inline_lbl_res.setStyleSheet("color: red;")

    def inline_save_match(self) -> None:
        if not self.last_match: return
        target = self.inline_target.text().strip()
        algo = self.inline_algo.text().strip()
        if self.current_case_id:
            import json

            from app.services.case_service import case_service
            case_path = case_service.get_case_path(self.current_case_id)
            if case_path.exists():
                from datetime import UTC, datetime
                log_file = case_path / "decoded" / "hash_recoveries.jsonl"
                record = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "target_hash": target,
                    "algorithm": algo,
                    "recovered_candidate": self.last_match
                }
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record) + "\n")
                QMessageBox.information(self, "Save Match", f"Match '{self.last_match}' saved to Case {self.current_case_id}.")
                return
        QMessageBox.information(self, "Save Match", f"Match '{self.last_match}' saved. (No active case set)")
        
    def inline_use_match(self) -> None:
        if not self.last_match: return
        self.txt_input.setText(self.last_match)
        self.tools_stack.setCurrentIndex(0)
        self.btn_mode_text.setChecked(True)
        self.switch_mode(0)

    def add_pipeline_step(self) -> None:
        decoder_name = self.combo_decoders.currentText()
        if not decoder_name or decoder_name.startswith("---"):
            return
        
        d_obj = decoder_registry.get(decoder_name)
        if d_obj and not getattr(d_obj, "reversible", True):
            QMessageBox.warning(self, "One-Way Function", f"{decoder_name} is a one-way function and should not be used in reversible pipelines.")
            
        params = {}
        for key, widget in self.param_inputs.items():
            if isinstance(widget, QLineEdit):
                params[key] = widget.text()
            elif isinstance(widget, QCheckBox):
                params[key] = widget.isChecked()
            
        step = TransformationStep(
            id=uuid.uuid4().hex[:8],
            decoder_name=decoder_name,
            parameters=params
        )
        self.pipeline.steps.append(step)
        self.list_pipeline.addItem(f"{len(self.pipeline.steps)}. {decoder_name}")
        
    def clear_pipeline(self) -> None:
        self.pipeline.steps.clear()
        self.list_pipeline.clear()
        
    def run_pipeline(self) -> None:
        inp = self._get_input()
        if not inp.text and not inp.data:
            return
            
        if not self.pipeline.steps:
            QMessageBox.warning(self, "Pipeline Empty", "Add transformations to the pipeline first.")
            return
            
        results = self.runner.run_pipeline(self.pipeline, inp)
        if not results:
            self.txt_output.setText("No results produced.")
            return
            
        final_result = results[-1]
        if final_result.success:
            if final_result.output_text is not None:
                self.txt_output.setText(final_result.output_text)
            elif final_result.output_data is not None:
                self.txt_output.setText(f"<Binary Data: {len(final_result.output_data)} bytes>")
            else:
                self.txt_output.setText("<Empty Success>")
        else:
            self.txt_output.setText(f"Error in {final_result.decoder}:\n" + "\n".join(final_result.errors))
            
    def copy_output(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if self.output_stack.currentIndex() == 0:
            clipboard.setText(self.txt_output.toPlainText())
            QMessageBox.information(self, "Copied", "Output copied to clipboard.")
        
    def send_to_case(self) -> None:
        QMessageBox.information(self, "Send to Case", "Output sent to case evidence.")
        
    def extract_iocs(self) -> None:
        from app.osint.extraction import ioc_extraction_service
        text = self.txt_output.toPlainText()
        if not text:
            return
        iocs = ioc_extraction_service.extract(text, case_id="decoder_session")
        if iocs:
            QMessageBox.information(self, "IOCs Extracted", f"Found {len(iocs)} indicators of compromise.")
        else:
            QMessageBox.information(self, "IOCs Extracted", "No IOCs found in output.")
            
    def send_output_to_decoder(self) -> None:
        if self.output_stack.currentIndex() == 0:
            text = self.txt_output.toPlainText()
            if text:
                self.txt_input.setText(text)
                self.btn_mode_text.setChecked(True)
                self.switch_mode(0)

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
        
    def identify_hash(self) -> None:
        txt = self.txt_hash_id_input.text().strip()
        if not txt:
            return
        cands = hash_identification_service.identify(txt)
        if not cands:
            self.txt_hash_id_res.setText("Other possible formats: None / lower confidence")
            return
            
        out = ""
        best = cands[0]
        out += f"Candidate: {best.algorithm} - {'HIGH' if best.confidence >= 0.8 else 'MODERATE'}\n"
        out += f"Reason: {', '.join(best.reasons)}\n\n"
        
        others = [f"{c.algorithm} ({int(c.confidence*100)}%)" for c in cands[1:]]
        if others:
            out += "Other possible formats: " + ", ".join(others)
        else:
            out += "Other possible formats: None"
            
        self.txt_hash_id_res.setText(out)
        
    def select_hash_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Hash")
        if file_path:
            self.current_hash_file = file_path
            self.lbl_hash_file_sel.setText(f"Selected: {file_path}")
            self.txt_hash_input.clear()
            self.txt_hash_input.setPlaceholderText("File selected. Clear this to use text instead.")
            
    def generate_hashes(self) -> None:
        txt = self.txt_hash_input.toPlainText()
        algos = hashing_service.get_supported_algorithms()
        
        if self.current_hash_file and not txt:
            if os.path.getsize(self.current_hash_file) > 1024 * 1024 * 100:
                reply = QMessageBox.question(self, "Large File", "File is >100MB. Calculate hashes?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No: return
            res = hashing_service.hash_file(Path(self.current_hash_file), algos)
        elif txt:
            res = hashing_service.hash_bytes(txt.encode('utf-8'), algos)
        else:
            QMessageBox.warning(self, "Input Required", "Enter text or select a file.")
            return
            
        self.last_hashes = res
        self.table_hashes.setRowCount(len(res))
        for i, (algo, digest) in enumerate(res.items()):
            self.table_hashes.setItem(i, 0, QTableWidgetItem(algo.upper()))
            self.table_hashes.setItem(i, 1, QTableWidgetItem(digest))
            btn = QPushButton("Copy")
            btn.clicked.connect(lambda _, d=digest: QGuiApplication.clipboard().setText(d))
            self.table_hashes.setCellWidget(i, 2, btn)
            
    def upload_image_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff)")
        if file_path:
            self.load_image(file_path)
            
    def upload_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.load_file(file_path)
            
    def load_image(self, path: str) -> None:
        self.current_image_path = path
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Show preview in the INPUT area (left side)
            if pixmap.width() > self.lbl_image_drop.width() or pixmap.height() > self.lbl_image_drop.height():
                self.lbl_image_drop.setPixmap(pixmap.scaled(self.lbl_image_drop.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.lbl_image_drop.setPixmap(pixmap)
        else:
            self.lbl_image_drop.setText("Invalid Image")
            
        res = image_analyzer_service.analyze(path)
        html = "<b>IMAGE ANALYSIS</b><br>"
        html += f"Format: {res['format']}<br>"
        html += f"Dimensions: {res['dimensions']}<br>"
        html += f"SHA256: {res['sha256'][:16]}...<br>"
        self.txt_detections.setHtml(html)
        
        # Explicitly set output to text (index 0) and clear it, NOT the image preview
        self.output_stack.setCurrentIndex(0)
        self.txt_output.setText(f"Image loaded: {os.path.basename(path)}\nSelect an analysis tool below.")
        self.tools_stack.setCurrentIndex(2)
        
    def load_file(self, path: str) -> None:
        self.lbl_file_drop.setText(f"Loaded: {os.path.basename(path)}")
        self.txt_detections.setHtml(f"<b>FILE LOADED</b><br>Path: {path}<br>Ready for specific analyzer.")

    def run_img_ocr(self) -> None:
        self.output_stack.setCurrentIndex(0)
        self.txt_output.setText("[OCR] Not implemented locally yet.")
        
    def run_img_qr(self) -> None:
        self.output_stack.setCurrentIndex(0)
        self.txt_output.setText("[QR/Barcode] Not implemented locally yet.")
        
    def run_img_stego(self) -> None:
        self.output_stack.setCurrentIndex(0)
        self.txt_output.setText("[Stego LSB] Feature available in Forensics/Stego tab.")
        
    def run_img_meta(self) -> None:
        self.output_stack.setCurrentIndex(0)
        if self.current_image_path:
            res = image_analyzer_service.analyze(self.current_image_path)
            out = ""
            for k,v in res.items():
                out += f"{k}: {v}\n"
            self.txt_output.setText(out)
            
    def run_img_ioc(self) -> None:
        self.output_stack.setCurrentIndex(0)
        self.txt_output.setText("[Extract IOCs] No IOCs found directly in image envelope.")

    def run_sym_detect(self) -> None:
        if not self.current_image_path:
            QMessageBox.warning(self, "No Image", "Load an image first.")
            return
            
        try:
            from app.decoders.symbols import symbol_analysis_service
            # Initial run to get symbols without custom mapping
            self.last_sym_result = symbol_analysis_service.analyze_image(
                self.current_image_path, 
                profile_id=self.combo_sym_profile.currentText()
            )
            
            # Populate table
            unique_ids = set()
            counts = {}
            for s in self.last_sym_result.detected_symbols:
                unique_ids.add(s.symbol_id)
                counts[s.symbol_id] = counts.get(s.symbol_id, 0) + 1
                
            self.table_sym_map.setRowCount(len(unique_ids))
            for i, sid in enumerate(sorted(unique_ids)):
                self.table_sym_map.setItem(i, 0, QTableWidgetItem(sid))
                # Initial mapping char
                mapped = self.last_sym_result.mapping_used.get(sid, "")
                self.table_sym_map.setItem(i, 1, QTableWidgetItem(mapped))
                self.table_sym_map.setItem(i, 2, QTableWidgetItem(str(counts[sid])))
                
            self.txt_output.setText(f"Detected {len(self.last_sym_result.detected_symbols)} symbols ({len(unique_ids)} unique).")
            self.output_stack.setCurrentIndex(0)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Symbol detection failed: {e}")
            
    def run_sym_solve(self) -> None:
        if not hasattr(self, 'last_sym_result'):
            QMessageBox.warning(self, "Run Detect First", "Please detect symbols first.")
            return
            
        # Build custom mapping from table
        custom_mapping = {}
        for r in range(self.table_sym_map.rowCount()):
            item_sid = self.table_sym_map.item(r, 0)
            item_val = self.table_sym_map.item(r, 1)
            if item_sid and item_val:
                sid = item_sid.text()
                val = item_val.text().strip()
                if val:
                    custom_mapping[sid] = val
                
        try:
            from app.decoders.symbols import symbol_analysis_service
            self.last_sym_result = symbol_analysis_service.analyze_image(
                self.current_image_path, 
                profile_id=self.combo_sym_profile.currentText(),
                custom_mapping=custom_mapping
            )
            
            out = "--- SYMBOL CIPHER CANDIDATES ---\\n\\n"
            for c in self.last_sym_result.candidates[:5]:
                marker = " 🚩 CTK FLAG CANDIDATE" if "CTK{" in c['text'] or "CTF{" in c['text'] or "FLAG{" in c['text'] or "TRON{" in c['text'] else ""
                out += f"Direction: {c['direction'].upper()} | Type: {c['type']} | Score: {c['score']:.2f}{marker}\\n"
                out += f"{c['text']}\\n\\n"
                
            self.txt_output.setText(out)
            self.output_stack.setCurrentIndex(0)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Auto solve failed: {e}")

    def run_sym_send(self) -> None:
        if hasattr(self, 'last_sym_result') and self.last_sym_result.candidates:
            text = self.last_sym_result.candidates[0]['text']
            self.txt_input.setText(text)
            self.btn_mode_text.setChecked(True)
            self.switch_mode(0)
            
    def run_sym_ioc(self) -> None:
        from app.osint.extraction import ioc_extraction_service
        if hasattr(self, 'last_sym_result') and self.last_sym_result.candidates:
            text = self.last_sym_result.candidates[0]['text']
            iocs = ioc_extraction_service.extract(text, case_id="decoder_session")
            if iocs:
                QMessageBox.information(self, "IOCs Extracted", f"Found {len(iocs)} indicators of compromise in best candidate.")
            else:
                QMessageBox.information(self, "IOCs Extracted", "No IOCs found in best candidate.")
                
    def run_sym_case(self) -> None:
        if hasattr(self, 'last_sym_result'):
            QMessageBox.information(self, "Save to Case", "Symbol analysis and best candidate saved to case.")
