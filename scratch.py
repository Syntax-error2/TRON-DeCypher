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
            html += ""<b>HASH DETECTED</b><br>""
            html += f""Algorithm: <b>{best.decoder_name}</b><br>""
            conf_str = ""HIGH"" if best.confidence >= 0.8 else (""MODERATE"" if best.confidence >= 0.5 else ""LOW"")
            html += f""Detection confidence: {conf_str}<br>""
            reasons = best.metadata.get('reasons', [])
            html += f""Reasons:<br>""
            for r in reasons:
                html += f""✓ {r}<br>""
            html += ""<br>""
            
            from app.crypto.hashes.hash_formats import hash_format_registry
            fmt = hash_format_registry.get(best.decoder_name.lower())
            if fmt:
                html += f""Family: {fmt.family}<br>""
                html += f""Digest size: {fmt.digest_length_hex * 4 if fmt.digest_length_hex else 'Variable'}-bit<br>""
                html += f""Encoding: {fmt.charset}<br>""
                html += f""Salted: {'Yes' if fmt.salt_support else 'No'}<br>""
                html += f""Structured: {'Yes' if fmt.is_structured else 'No'}<br>""
                html += f""Recovery: {fmt.security_notes}<br><br>""
                
            html += ""<i>This value cannot be mathematically decoded.</i><br>""
            html += f""Actions: <a href='hash:{best.decoder_name}'>[Recover Hash]</a> <a href='hash:{best.decoder_name}'>[Verify Candidate]</a><br><br>""
            
        if enc_cands:
            html += ""<b>OTHER INTERPRETATIONS</b><br>""
            for c in enc_cands[:3]:
                conf_str = ""HIGH"" if c.confidence >= 0.8 else (""MODERATE"" if c.confidence >= 0.5 else ""LOW"")
                html += f""• {c.decoder_name} (Confidence: {conf_str}) - <a href='enc:{c.decoder_name}'>[Apply]</a><br>""
                
        self.txt_detections.setHtml(html)
