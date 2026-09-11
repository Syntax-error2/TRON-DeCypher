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
            html += f"<b>Method:</b> CTF Dictionary<br>"
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
                QMessageBox.information(self, "Flag Detected", f"Potential Flag Recovered:\n" + "\n".join(flags))
                
        elif status == "CANCELLED":
            self.inline_lbl_res.setText("Result: CANCELLED")
            self.inline_lbl_res.setStyleSheet("color: red;")
        else:
            time_elapsed = data.get("elapsed", 0)
            count = data.get("count", 0)
            
            html = "<b>NO MATCH FOUND</b><br><br>"
            html += f"<b>Algorithm:</b> {self.inline_algo.text()}<br>"
            html += f"<b>Sources:</b> Built-in CTF dictionary, Mutations, Patterns<br>"
            html += f"<b>Candidates checked:</b> {count}<br>"
            html += f"<b>Time:</b> {time_elapsed:.2f}s<br><br>"
            html += "<b>Possible next step:</b><br>"
            html += "- Add a local wordlist.<br>"
            html += "- Change bounded recovery options.<br>"
            html += "- Inspect challenge context.<br>"
            
            self.txt_detections.setHtml(html)
            self.inline_lbl_res.setText("Result: NO MATCH FOUND")
            self.inline_lbl_res.setStyleSheet("color: red; font-weight: bold;")
