    def recover_automatic_generator(self, target_hash: str, algorithm: str) -> Iterator[dict[str, Any]]:
        start_time = time.time()
        target_hash = target_hash.strip().lower()
        algorithm = algorithm.lower()
        
        if algorithm not in hashlib.algorithms_available:
            yield {"status": "ERROR", "msg": f"Unsupported algorithm: {algorithm}"}
            return
            
        built_in_dict = [
            "hello", "admin", "password", "secret", "flag", "test", 
            "root", "guest", "welcome", "qwerty", "123456", "letmein",
            "administrator", "changeme"
        ]
        
        mutations = []
        for word in built_in_dict:
            mutations.append(word)
            mutations.append(word.capitalize())
            mutations.append(word.upper())
            mutations.append(word + "123")
            mutations.append(word + "2026")
            mutations.append(word.replace("a", "@").replace("e", "3").replace("i", "1").replace("o", "0"))
            
        count = 0
        yield {"status": "RUNNING", "count": count, "elapsed": time.time() - start_time, "source": "built-in dictionary + mutations"}
        
        for candidate in mutations:
            count += 1
            h = hashlib.new(algorithm)
            h.update(candidate.encode('utf-8'))
            if hmac.compare_digest(h.hexdigest().lower(), target_hash):
                
                is_flag = candidate.upper().startswith("TRON{") or candidate.upper().startswith("FLAG{")
                
                yield {
                    "status": "MATCH",
                    "candidate": candidate,
                    "count": count,
                    "elapsed": time.time() - start_time,
                    "source": "built-in dictionary",
                    "is_flag": is_flag
                }
                return
                
        yield {
            "status": "NO_MATCH",
            "count": count,
            "elapsed": time.time() - start_time,
            "source": "built-in + mutations"
        }
