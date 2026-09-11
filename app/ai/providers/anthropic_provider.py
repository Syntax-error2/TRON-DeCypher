import json
import logging
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

from app.ai.models.models import AIAnalysisResponse, Recommendation
from app.ai.providers.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class AnthropicProvider(AIProvider):
    def name(self) -> str:
        return "Anthropic"
        
    def is_configured(self) -> bool:
        return bool(settings.anthropic_api_key)
        
    def _validate_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ["https", "http"]:
                return False
            if parsed.scheme == "http":
                # Only allow http for local dev
                if parsed.hostname not in ["localhost", "127.0.0.1", "::1"]:
                    return False
            return True
        except Exception:
            return False

    def analyze(self, system_prompt: str, user_prompt: str) -> AIAnalysisResponse:
        if not self.is_configured():
            return AIAnalysisResponse(summary="Anthropic API Key not configured.", confidence="Low")
            
        base_url = settings.anthropic_base_url or "https://api.anthropic.com/v1"
        if not self._validate_url(base_url):
            logger.error("Invalid Anthropic Base URL configured.")
            return AIAnalysisResponse(summary="Configuration Error: Invalid base URL.", confidence="Low")
            
        url = f"{base_url.rstrip('/')}/messages"
        
        headers = {
            "x-api-key": settings.anthropic_api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        full_sys_prompt = system_prompt + "\n\nYou MUST respond in strictly valid JSON matching this schema:\n"
        full_sys_prompt += '{"summary": "...", "observations": ["..."], "evidence_citations": ["..."], "confidence": "High|Medium|Low", "recommendations": [{"action": "...", "reason": "...", "evidence": "...", "module": "...", "confidence": "..."}]}'
        
        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_output_tokens,
            "temperature": self.config.temperature,
            "system": full_sys_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        retries = 3
        backoff = 1.0
        
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
                start_time = time.time()
                with urllib.request.urlopen(req, timeout=self.config.request_timeout) as response:
                    duration = time.time() - start_time
                    logger.info(f"Anthropic API Success: model={self.config.model} duration={duration:.2f}s status={response.status}")
                    result = json.loads(response.read().decode("utf-8"))
                    text_out = result["content"][0]["text"]
                    
                    try:
                        clean_text = text_out.strip()
                        if clean_text.startswith("`" + "json"):
                            clean_text = clean_text[7:]
                        if clean_text.endswith("`" + ""):
                            clean_text = clean_text[:-3]
                            
                        parsed = json.loads(clean_text)
                        recs = []
                        for r in parsed.get("recommendations", []):
                            recs.append(Recommendation(
                                action=r.get("action", ""),
                                reason=r.get("reason", ""),
                                evidence=r.get("evidence", ""),
                                module=r.get("module", ""),
                                confidence=r.get("confidence", "Low")
                            ))
                            
                        return AIAnalysisResponse(
                            summary=parsed.get("summary", ""),
                            observations=parsed.get("observations", []),
                            evidence_citations=parsed.get("evidence_citations", []),
                            confidence=parsed.get("confidence", "Unknown"),
                            recommendations=recs
                        )
                        
                    except json.JSONDecodeError:
                        return AIAnalysisResponse(
                            summary="Failed to parse structured JSON from provider. Raw output:\n" + text_out,
                            confidence="Low"
                        )
                        
            except urllib.error.HTTPError as e:
                if e.code in [429, 502, 503] and attempt < retries - 1:
                    logger.warning(f"Anthropic API transient error {e.code}, retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    logger.error(f"Anthropic API Error: status={e.code}")
                    return AIAnalysisResponse(summary=f"API HTTP Error: {e.code} {e.reason}", confidence="Low")
            except urllib.error.URLError as e:
                logger.error(f"Anthropic Network Error: {e.reason}")
                return AIAnalysisResponse(summary=f"Network Error: {e.reason}", confidence="Low")
            except Exception as e:
                logger.error(f"Unexpected AI Error: type={type(e).__name__}")
                return AIAnalysisResponse(summary=f"Unexpected Error: {e}", confidence="Low")
                
        return AIAnalysisResponse(summary="Max retries exceeded.", confidence="Low")


