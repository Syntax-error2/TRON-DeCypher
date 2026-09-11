import time
import uuid

from app.ai.context.builder import ai_context_builder
from app.ai.models.models import AIAnalysisResponse, AIProviderConfig
from app.ai.prompts.templates import ANALYST_ASSISTANT_SYSTEM_PROMPT, EXPLAIN_FINDING_PROMPT
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.base import AIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.safety.redactor import ai_redactor
from app.core.config import settings
from app.database.database import db


class CopilotService:
    def __init__(self) -> None:
        self.config = AIProviderConfig()
        self.provider: AIProvider = MockAIProvider(self.config)
        self.refresh_config()
        
    def refresh_config(self) -> None:
        self.config.api_key_configured = bool(settings.anthropic_api_key)
        self.config.provider = "Anthropic" if settings.anthropic_api_mode == "External" else "Mock"
        self.config.model = settings.anthropic_model or "claude-3-opus-20240229"
        self.config.base_url = settings.anthropic_base_url or ""
        self.config.temperature = settings.anthropic_temperature
        self.config.max_output_tokens = settings.anthropic_max_tokens
        self.config.request_timeout = settings.anthropic_timeout
        self.config.enabled = True
        
        if self.config.provider == "Anthropic":
            self.provider = AnthropicProvider(self.config)
        else:
            self.provider = MockAIProvider(self.config)
            
    def is_available(self) -> bool:
        return self.config.enabled
        
    def explain_finding(self, finding_id: str, artifact_id: str) -> AIAnalysisResponse:
        if not self.is_available():
            return AIAnalysisResponse(summary="AI is disabled or not configured.")
            
        context = ai_context_builder.build_artifact_context(artifact_id)
        
        finding_text = f"Finding ID: {finding_id}"
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM findings WHERE id = ?", (finding_id,))
            f = cursor.fetchone()
            if f:
                finding_text = f"[{f['severity']}] {f['title']}: {f['description']}"
                
        user_prompt = EXPLAIN_FINDING_PROMPT.format(
            finding_text=finding_text,
            context=context.text_content
        )
        
        response = self.provider.analyze(ANALYST_ASSISTANT_SYSTEM_PROMPT, user_prompt)
        self._persist_history(artifact_id, user_prompt, response)
        
        return response
        
    def custom_query(self, artifact_id: str, query: str) -> AIAnalysisResponse:
        if not self.is_available():
            return AIAnalysisResponse(summary="AI is disabled or not configured.")
            
        context = ai_context_builder.build_artifact_context(artifact_id)
        
        # CTF Knowledge Search
        from app.knowledge.knowledge_service import knowledge_service
        kn_results = knowledge_service.search(query)
        kn_context = ""
        if kn_results:
            kn_context = "Relevant CTF Knowledge References:\n"
            for r in kn_results[:3]:
                kn_context += f"Source: {r['source']} (Page {r['page']}, Section: {r['section']})\n"
                kn_context += f"Topic: {r['topic']}\n"
                kn_context += f"Summary: {r['text']}\n\n"
        else:
            kn_context = "No matching material was found in the imported references.\n"
            
        user_prompt = f"{kn_context}\nContext:\n{context.text_content}\n\nUser Question:\n{query}\n\nINSTRUCTION: Always cite the exact source document, page, and section when using the provided CTF Knowledge. If no material is found, explicitly state 'No matching material was found in the imported references.' Do not fabricate source citations."
        
        response = self.provider.analyze(ANALYST_ASSISTANT_SYSTEM_PROMPT, user_prompt)
        
        if "Mock" in self.config.provider:
            if not kn_results:
                response.summary = "No matching material was found in the imported references."
            else:
                response.summary = f"Based on the provided references:\n\nSource: {kn_results[0]['source']}\nPage: {kn_results[0]['page']}\nSection: {kn_results[0]['section']}\n\n" + response.summary
                
        self._persist_history(artifact_id, query, response)
        return response
        
    def test_connection(self) -> str:
        if self.config.provider != "Anthropic":
            return "Connection successful (Mock Mode)."
            
        if not self.provider.is_configured():
            return "Connection failed: API Key not configured."
            
        # Minimal harmless request
        response = self.provider.analyze("You are a helpful assistant.", "Please reply with 'OK' if you can hear me. Say nothing else.")
        if "OK" in response.summary or response.confidence != "Low":
            return "Connection successful."
        else:
            return f"Connection failed: {response.summary}"
            
    def _persist_history(self, artifact_id: str, query: str, response: AIAnalysisResponse) -> None:
        safe_query = ai_redactor.redact(query)
        msg_id = str(uuid.uuid4())
        ts = time.time()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ai_messages (id, artifact_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (msg_id, artifact_id, 'user', safe_query, ts))
            
            resp_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO ai_messages (id, artifact_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (resp_id, artifact_id, 'assistant', response.summary, ts))
            conn.commit()

copilot_service = CopilotService()
