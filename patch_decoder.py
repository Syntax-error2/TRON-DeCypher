import re

with open('app/ui/views/decoder_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
        html = "<b>AUTO-DETECTION</b><br>"
        for d in detections:
            scheme = d.decoder_id
            name = d.name
            conf = d.confidence
            html += f"<a href='{scheme}'>{name}</a> ({int(conf*100)}%)<br>"
            
        # CTF Knowledge Integration
        from app.knowledge.knowledge_service import knowledge_service
        # Use top detection to query knowledge
        if detections:
            top_name = detections[0].name
            kn = knowledge_service.search(top_name)
            if kn:
                html += "<br><b>Related CTF Knowledge:</b><br>"
                html += f"Topic: {kn[0]['topic']}<br>"
                html += f"Source: {kn[0]['source']}<br>"

        self.txt_detections.setHtml(html)
'''
content = content.replace('''
        html = "<b>AUTO-DETECTION</b><br>"
        for d in detections:
            scheme = d.decoder_id
            name = d.name
            conf = d.confidence
            html += f"<a href='{scheme}'>{name}</a> ({int(conf*100)}%)<br>"
            
        self.txt_detections.setHtml(html)
''', patch)

with open('app/ui/views/decoder_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
