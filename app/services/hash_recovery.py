import hashlib
import hmac
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.knowledge.challenge_context import context_manager
from app.knowledge.flag_detection import flag_detection_service
from app.knowledge.registry import knowledge_registry
from app.services.candidate_generation import CandidateConfig, CandidateGenerator


def utc_now() -> datetime:
    return datetime.now(UTC)

class HashRecoveryResult(BaseModel):
    target_hash: str
    algorithm: str
    status: str
    candidate: str | None = None
    candidate_count: int = 0
    elapsed_time: float = 0.0
    method: str
    source_wordlist: str | None = None
    evidence_reference: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)

class HashRecoveryService:
    def verify_candidate(self, target_hash: str, algorithm: str, candidate: str) -> HashRecoveryResult:
        start_time = time.time()
        target_hash = target_hash.strip().lower()
        algorithm = algorithm.lower()
        
        if algorithm not in hashlib.algorithms_available:
            return HashRecoveryResult(
                target_hash=target_hash, algorithm=algorithm, status="ERROR",
                method="Candidate", candidate_count=1, elapsed_time=time.time() - start_time
            )
            
        h = hashlib.new(algorithm)
        h.update(candidate.encode('utf-8'))
        digest = h.hexdigest().lower()
        
        match = hmac.compare_digest(digest, target_hash)
        
        return HashRecoveryResult(
            target_hash=target_hash,
            algorithm=algorithm,
            status="MATCH" if match else "NO_MATCH",
            candidate=candidate if match else None,
            method="Candidate",
            candidate_count=1,
            elapsed_time=time.time() - start_time
        )
        
    def recover_wordlist_generator(self, target_hash: str, algorithm: str, wordlist_path: Path) -> Iterator[dict[str, Any]]:
        # keep this for compatibility if anything calls it directly, though we should prefer automatic
        start_time = time.time()
        target_hash = target_hash.strip().lower()
        algorithm = algorithm.lower()
        
        if algorithm not in hashlib.algorithms_available:
            yield {"status": "ERROR", "msg": f"Unsupported algorithm: {algorithm}"}
            return
            
        count = 0
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    candidate = line.strip('\n').removesuffix('\r')
                    candidates_to_try = [candidate, candidate.lower(), candidate.upper()]
                    
                    for cand in set(candidates_to_try):
                        count += 1
                        h = hashlib.new(algorithm)
                        h.update(cand.encode('utf-8'))
                        if hmac.compare_digest(h.hexdigest().lower(), target_hash):
                            flags = flag_detection_service.detect(cand, "Hash Recovery")
                            yield {
                                "status": "MATCH",
                                "candidate": cand,
                                "count": count,
                                "elapsed": time.time() - start_time,
                                "source": wordlist_path.name,
                                "strategy": "Wordlist exact/case",
                                "is_flag": len(flags) > 0,
                                "flags": [f.value for f in flags]
                            }
                            return
                            
                    if count % 10000 == 0:
                        yield {
                            "status": "RUNNING",
                            "count": count,
                            "rate": count / max(0.001, time.time() - start_time),
                            "elapsed": time.time() - start_time,
                            "source": wordlist_path.name,
                            "strategy": "Wordlist exact/case"
                        }
                        
        except Exception as e:
            yield {"status": "ERROR", "msg": str(e)}
            return
            
        yield {
            "status": "NO_MATCH",
            "count": count,
            "elapsed": time.time() - start_time,
            "source": wordlist_path.name,
            "strategy": "Wordlist exact/case"
        }

    def recover_automatic_generator(self, target_hash: str, algorithm: str, config: CandidateConfig = None) -> Iterator[dict[str, Any]]:
        start_time = time.time()
        target_hash = target_hash.strip().lower()
        algorithm = algorithm.lower()
        
        if algorithm not in hashlib.algorithms_available:
            yield {"status": "ERROR", "msg": f"Unsupported algorithm: {algorithm}"}
            return
            
        if config is None:
            config = CandidateConfig()
            
        master_words = knowledge_registry.get_master_wordlist()
        tron_words = knowledge_registry.get_tron_context_wordlist()
        cat_words = []
        category = context_manager.current_context.category
        if category and category != "Misc":
            cat_words = knowledge_registry.get_category_wordlist(category)
            
        generator = CandidateGenerator(config)
        iterator = generator.generate(master_words, tron_words, cat_words)
        
        count = 0
        yield {"status": "RUNNING", "count": count, "rate": 0.0, "elapsed": 0.0, "source": "Init", "strategy": "Init"}
        
        for cand in iterator:
            count += 1
            if count > config.max_candidates:
                yield {"status": "LIMIT_REACHED", "msg": "Maximum candidates reached.", "count": count, "elapsed": time.time() - start_time, "source": cand.source, "strategy": cand.mutation}
                return
                
            elapsed = time.time() - start_time
            if elapsed > config.max_runtime_sec:
                yield {"status": "LIMIT_REACHED", "msg": "Maximum runtime reached.", "count": count, "elapsed": elapsed, "source": cand.source, "strategy": cand.mutation}
                return
                
            h = hashlib.new(algorithm)
            h.update(cand.value.encode('utf-8'))
            if hmac.compare_digest(h.hexdigest().lower(), target_hash):
                flags = flag_detection_service.detect(cand.value, "Hash Recovery")
                yield {
                    "status": "MATCH",
                    "candidate": cand.value,
                    "count": count,
                    "elapsed": time.time() - start_time,
                    "source": cand.source,
                    "strategy": cand.mutation,
                    "is_flag": len(flags) > 0,
                    "flags": [f.value for f in flags]
                }
                return
                
            if count % 20000 == 0:
                yield {
                    "status": "RUNNING",
                    "count": count,
                    "rate": count / max(0.001, elapsed),
                    "elapsed": elapsed,
                    "source": cand.source,
                    "strategy": cand.mutation
                }
                
        yield {
            "status": "NO_MATCH",
            "count": count,
            "elapsed": time.time() - start_time,
            "source": "Exhausted",
            "strategy": "Exhausted"
        }

hash_recovery_service = HashRecoveryService()
