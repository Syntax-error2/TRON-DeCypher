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
            
            html = f""<b>✓ HASH RECOVERED</b><br><br>""
            html += f""Algorithm: {self.inline_algo.text()}<br>""
            html += f""Hash: {self.inline_target.text()}<br>""
            html += f""Recovered: <b>{cand}</b><br>""
            html += f""Method: {source}<br>""
            html += f""Candidates checked: {count}<br>""
            html += f""Time: {time_elapsed:.2f}s<br>""
            
            self.inline_lbl_res.setText("Result: ✓ MATCH")
            self.inline_lbl_res.setStyleSheet("color: green; font-weight: bold;")
            
            # Put the rich text into a message box since the inline UI doesn't have space for all this
            QMessageBox.information(self, "Hash Recovered", html.replace("<br>", "\n").replace("<b>", "").replace("</b>", ""))
            
            self.last_match = cand
            self.inline_btn_save.setEnabled(True)
            self.inline_btn_send.setEnabled(True)
            if data.get("is_flag"):
                QMessageBox.information(self, "Flag Detected", f"Potential Flag Recovered: {cand}")
        elif status == "CANCELLED":
            self.inline_lbl_res.setText("Result: CANCELLED")
            self.inline_lbl_res.setStyleSheet("color: red;")
        else:
            time_elapsed = data.get("elapsed", 0)
            count = data.get("count", 0)
            
            html = f""<b>NO MATCH FOUND</b><br><br>""
            html += f""Algorithm: {self.inline_algo.text()}<br>""
            html += f""Candidates checked: {count}<br>""
            html += f""Time: {time_elapsed:.2f}s<br><br>""
            html += ""Suggested:<br>""
            html += ""- Add a wordlist<br>""
            html += ""- Change bounded recovery options<br>""
            html += ""- Inspect challenge context<br>""
            
            self.inline_lbl_res.setText("Result: NO MATCH FOUND")
            self.inline_lbl_res.setStyleSheet("color: red; font-weight: bold;")
            
            QMessageBox.warning(self, "No Match", html.replace("<br>", "\n").replace("<b>", "").replace("</b>", ""))
