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
