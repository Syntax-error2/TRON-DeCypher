import hashlib
import logging
import zlib
from pathlib import Path

logger = logging.getLogger(__name__)

class HashingService:
    """Calculates cryptographic hashes using a streaming approach for memory safety."""
    
    CHUNK_SIZE = 65536  # 64 KB
    
    @staticmethod
    def get_supported_algorithms() -> list[str]:
        # Guarantee these common algorithms are available
        return ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s", "crc32"]
        
    def hash_file(self, file_path: Path, algorithms: list[str] | None = None) -> dict[str, str]:
        """Hashes a file using one or more algorithms simultaneously."""
        if algorithms is None:
            algorithms = ["md5", "sha256"]
            
        hashers = {}
        do_crc32 = False
        crc_val = 0
        
        for algo in algorithms:
            if algo.lower() == "crc32":
                do_crc32 = True
            elif algo.lower() in hashlib.algorithms_available:
                hashers[algo.lower()] = hashlib.new(algo.lower())
            else:
                logger.warning(f"Hash algorithm {algo} is not available on this system.")
                
        with open(file_path, "rb") as f:
            while chunk := f.read(self.CHUNK_SIZE):
                for h in hashers.values():
                    h.update(chunk)
                if do_crc32:
                    crc_val = zlib.crc32(chunk, crc_val)
                    
        res = {algo: h.hexdigest() for algo, h in hashers.items()}
        if do_crc32:
            res["crc32"] = f"{crc_val & 0xFFFFFFFF:08x}"
        return res
        
    def hash_bytes(self, data: bytes, algorithms: list[str] | None = None) -> dict[str, str]:
        """Hashes an in-memory byte array."""
        if algorithms is None:
            algorithms = ["md5", "sha256"]
        results = {}
        for algo in algorithms:
            if algo.lower() == "crc32":
                results["crc32"] = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
            elif algo.lower() in hashlib.algorithms_available:
                h = hashlib.new(algo.lower())
                h.update(data)
                results[algo.lower()] = h.hexdigest()
        return results

hashing_service = HashingService()
