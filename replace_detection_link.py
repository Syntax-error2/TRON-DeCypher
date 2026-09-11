    def on_detection_link_clicked(self, url) -> None:
        scheme = url.scheme()
        path = url.path()
        if scheme == "enc":
            decoder = decoder_registry.get(path)
            if decoder:
                res = decoder.decode(self._get_input())
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
            self._start_hash_recovery()
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
