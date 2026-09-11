import re

with open('app/ai/services/copilot_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
    def custom_query(self, artifact_id: str, query: str) -> AIAnalysisResponse:
        if not self.is_available():
            return AIAnalysisResponse(summary="AI is disabled or not configured.")
            
        context = ai_context_builder.build_artifact_context(artifact_id)
        
        # CTF Knowledge Search
        from app.knowledge.knowledge_service import knowledge_service
        kn_results = knowledge_service.search(query)
        kn_context = ""
        if kn_results:
            kn_context = "Relevant CTF Knowledge References:\\n"
            for r in kn_results[:3]:
                kn_context += f"Source: {r['source']} (Page {r['page']}, Section: {r['section']})\\n"
                kn_context += f"Topic: {r['topic']}\\n"
                kn_context += f"Summary: {r['text']}\\n\\n"
        else:
            kn_context = "No matching material was found in the imported references.\\n"
            
        user_prompt = f"{kn_context}\\nContext:\\n{context.text_content}\\n\\nUser Question:\\n{query}\\n\\nINSTRUCTION: Always cite the exact source document, page, and section when using the provided CTF Knowledge. If no material is found, explicitly state 'No matching material was found in the imported references.' Do not fabricate source citations."
        
        response = self.provider.analyze(ANALYST_ASSISTANT_SYSTEM_PROMPT, user_prompt)
        
        if "Mock" in self.config.provider:
            if not kn_results:
                response.summary = "No matching material was found in the imported references."
            else:
                response.summary = f"Based on the provided references:\\n\\nSource: {kn_results[0]['source']}\\nPage: {kn_results[0]['page']}\\nSection: {kn_results[0]['section']}\\n\\n" + response.summary
                
        self._persist_history(artifact_id, query, response)
        return response
'''
# Using exact string replacement to fix the broken block
def fix_service():
    lines = content.splitlines()
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("    def custom_query(self,"):
            start_idx = i
            break
            
    if start_idx != -1:
        end_idx = -1
        for i in range(start_idx + 1, len(lines)):
            if lines[i].startswith("    def test_connection"):
                end_idx = i
                break
        
        if end_idx != -1:
            new_lines = lines[:start_idx] + patch.strip().splitlines() + [''] + lines[end_idx:]
            with open('app/ai/services/copilot_service.py', 'w', encoding='utf-8') as f:
                f.write('\\n'.join(new_lines))

fix_service()
