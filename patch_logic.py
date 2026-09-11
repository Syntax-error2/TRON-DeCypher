import re
with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to remove inline_toggle_method and its connection
content = re.sub(r'        self\.inline_radio_cand\.toggled\.connect\(self\.inline_toggle_method\)\n        self\.inline_toggle_method\(\)\n', '', content)
content = re.sub(r'    def inline_toggle_method\(self\) -> None:\n(?:        .*?\n)*', '', content)

patch_logic = '''
    def preview_candidates(self):
        from app.services.candidate_generation import CandidateConfig, CandidateGenerator
        from app.knowledge.registry import knowledge_registry
        from app.knowledge.challenge_context import context_manager
        
        config = CandidateConfig(
            max_candidates=100,
            max_runtime_sec=5.0,
            enable_leetspeak=self.chk_leet.isChecked(),
            enable_mixed_case=self.chk_case.isChecked(),
            enable_digit_suffix=self.chk_num.isChecked(),
            enable_wrappers=self.chk_wrap.isChecked(),
            max_combination_depth=self.spin_depth.value()
        )
        
        master_words = knowledge_registry.get_master_wordlist()
        tron_words = knowledge_registry.get_tron_context_wordlist()
        cat_words = []
        category = context_manager.current_context.category
        if category and category != "Misc":
            cat_words = knowledge_registry.get_category_wordlist(category)
            
        generator = CandidateGenerator(config)
        
        from PySide6.QtWidgets import QMessageBox
        preview = []
        try:
            iterator = generator.generate(master_words, tron_words, cat_words)
            for c in iterator:
                preview.append(f"{c.value} (Prio: {c.priority}, Src: {c.source}, Mut: {c.mutation})")
                if len(preview) >= 100:
                    break
            QMessageBox.information(self, "Candidate Preview (Top 100)", "\\n".join(preview))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Preview failed: {e}")

    def inline_start_recovery(self) -> None:
        target = self.inline_target.text().strip()
        algo = self.inline_algo.text().strip()
        
        if not target:
            return
            
        self.last_match = None
        self.inline_btn_save.setEnabled(False)
        self.inline_btn_send.setEnabled(False)
        self.inline_btn_start.setEnabled(False)
        self.inline_btn_cancel.setEnabled(True)
        
        from app.services.candidate_generation import CandidateConfig
        config = CandidateConfig(
            max_candidates=self.spin_max_cands.value(),
            max_runtime_sec=self.spin_max_time.value(),
            enable_leetspeak=self.chk_leet.isChecked(),
            enable_mixed_case=self.chk_case.isChecked(),
            enable_digit_suffix=self.chk_num.isChecked(),
            enable_wrappers=self.chk_wrap.isChecked(),
            max_combination_depth=self.spin_depth.value()
        )
        
        self.inline_lbl_res.setText("Result: RUNNING...")
        self.inline_lbl_res.setStyleSheet("color: orange; font-weight: bold;")
        
        self.recovery_worker = HashRecoveryWorker(target, algo, None, config)
        self.recovery_worker.progress.connect(self.inline_update_progress)
        self.recovery_worker.finished_ok.connect(self.inline_recovery_finished)
        self.recovery_worker.error.connect(self.inline_recovery_error)
        self.recovery_worker.start()

    def inline_update_progress(self, msg: str) -> None:
        self.inline_lbl_prog.setText(f"Progress: {msg}")

    def inline_recovery_finished(self, msg: str) -> None:
        self.inline_btn_start.setEnabled(True)
        self.inline_btn_cancel.setEnabled(False)
        self.inline_lbl_prog.setText("Progress: Finished")
        
        # Parse the output
        if "MATCH" in msg or "RECOVERED" in msg:
            self.inline_lbl_res.setText(f"Result: {msg}")
            self.inline_lbl_res.setStyleSheet("color: green; font-weight: bold;")
            import re
            m = re.search(r"Value:\s*(.+)", msg)
            if m:
                self.last_match = m.group(1).strip()
                self.inline_btn_save.setEnabled(True)
                self.inline_btn_send.setEnabled(True)
        else:
            self.inline_lbl_res.setText(msg)
            self.inline_lbl_res.setStyleSheet("color: red; font-weight: bold;")
            
    def inline_recovery_error(self, err: str) -> None:
        self.inline_btn_start.setEnabled(True)
        self.inline_btn_cancel.setEnabled(False)
        self.inline_lbl_res.setText(f"Result: ERROR - {err}")
        self.inline_lbl_res.setStyleSheet("color: red; font-weight: bold;")

    def inline_cancel_recovery(self) -> None:
        if hasattr(self, 'recovery_worker') and self.recovery_worker.isRunning():
            self.recovery_worker.cancel()
            self.inline_lbl_res.setText("Result: CANCELLED")
            self.inline_lbl_res.setStyleSheet("color: red; font-weight: bold;")
            self.inline_btn_start.setEnabled(True)
            self.inline_btn_cancel.setEnabled(False)
'''

# Find the start of inline_start_recovery
start_idx = content.find("    def inline_start_recovery(self) -> None:")
end_idx = content.find("    def inline_browse_wordlist(self) -> None:")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + patch_logic.strip('\n') + '\n\n' + content[end_idx:]
    # Now patch HashRecoveryWorker definition!
    worker_patch = '''
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
                    res_str = f"o" RECOVERED\\nValue: {c}"
                    if flags:
                        res_str += f"\\nFLAG CANDIDATE: {flags[0]}"
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
'''
    # Replace existing HashRecoveryWorker
    w_start = content.find("class HashRecoveryWorker(QThread):")
    w_end = content.find("class DecoderView(QWidget):")
    if w_start != -1 and w_end != -1:
        content = content[:w_start] + worker_patch.strip('\n') + '\n\n' + content[w_end:]

    with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched logic in decoder_view.py")
else:
    print("Could not find method bounds")
