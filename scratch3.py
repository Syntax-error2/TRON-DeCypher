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
            html += ""<b>HASH DETECTED</b><br><br>""
            html += f""<b>Algorithm:</b> {best.decoder_name}<br>""
            
            fmt = hash_format_registry.get(best.decoder_name.lower())
            if fmt:
                html += f""<b>Digest:</b> {fmt.digest_length_hex * 4 if fmt.digest_length_hex else 'Variable'}-bit<br>""
                html += f""<b>Representation:</b> {'Hexadecimal' if fmt.charset == 'hex' else 'Base64/Structured'}<br>""
                html += f""<b>Length:</b> {len(inp.text.strip())}<br>""
                html += f""<b>Salt:</b> {'Indicated' if fmt.salt_support else 'Not indicated'}<br>""
                html += f""<b>Structured:</b> {'Yes' if fmt.is_structured else 'No'}<br>""
            
            conf_str = ""HIGH"" if best.confidence >= 0.8 else (""MODERATE"" if best.confidence >= 0.5 else ""LOW"")
            html += f""<b>Detection confidence:</b> {conf_str}<br>""
            
            ambig = ""None""
            if len(hash_cands) > 1:
                ambig = ""Other candidate formats: "" + "", "".join([c.decoder_name for c in hash_cands[1:4]])
                
            html += f""<b>Possible ambiguity:</b> {ambig}<br>""
            if fmt:
                html += f""<b>Recovery:</b> {fmt.security_notes}<br>""
            
            html += ""<br><b>Reasons:</b><br>""
            reasons = best.metadata.get('reasons', [])
            for r in reasons:
                html += f""✓ {r}<br>""
            html += ""<br>""
            
            html += ""<i>This value cannot be mathematically decoded.</i><br>""
            html += f""Actions: <a href='hash:{best.decoder_name}'>[Recover Hash]</a> <a href='hash:{best.decoder_name}'>[Verify Candidate]</a><br><br>""
            
        if enc_cands:
            html += ""<b>OTHER INTERPRETATIONS</b><br>""
            for c in enc_cands[:3]:
                conf_str = ""HIGH"" if c.confidence >= 0.8 else (""MODERATE"" if c.confidence >= 0.5 else ""LOW"")
                html += f""• {c.decoder_name} (Confidence: {conf_str}) - <a href='enc:{c.decoder_name}'>[Apply]</a><br>""
                
        self.txt_detections.setHtml(html)
