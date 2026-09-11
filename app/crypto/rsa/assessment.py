import time
from typing import Any

from app.crypto.models import CryptoResult
from app.crypto.rsa.factorization import bounded_factorization
from app.crypto.rsa.number_theory import euler_phi, mod_inverse


class RSAAssessmentService:
    """Diagnoses RSA parameters (n, e, c) for known mathematical CTF vulnerabilities."""
    
    def assess(self, n: int | None = None, e: int | None = None, c: int | None = None, 
               p: int | None = None, q: int | None = None, d: int | None = None) -> CryptoResult:
        
        start_time = time.time()
        observations = []
        parameters: dict[str, Any] = {}
        
        # Track what we know
        if n: parameters["n"] = n
        if e: parameters["e"] = e
        if c: parameters["c"] = c
        if p: parameters["p"] = p
        if q: parameters["q"] = q
        if d: parameters["d"] = d
        
        # 1. If we have p and q, calculate n, phi, d
        if p and q:
            if not n:
                n = p * q
                parameters["n"] = n
                observations.append("Calculated n from p and q.")
            
            phi = euler_phi(p, q)
            parameters["phi"] = phi
            
            if e and not d:
                try:
                    d = mod_inverse(e, phi)
                    parameters["d"] = d
                    observations.append("Calculated private exponent d from p, q, and e.")
                except ValueError:
                    observations.append("Could not calculate d: e and phi are not coprime!")
                    
        # 2. Check Modulus Size
        if n:
            bit_length = n.bit_length()
            parameters["n_bit_length"] = bit_length
            if bit_length < 256:
                observations.append(f"Modulus is very small ({bit_length} bits). Easily factorable.")
            elif bit_length < 1024:
                observations.append(f"Modulus is dangerously small ({bit_length} bits). Vulnerable to standard factoring.")
                
        # 3. Check E Size
        if e:
            if e == 3:
                observations.append("e = 3. Vulnerable to cube root attack if padding is improper, or Hastad's Broadcast attack.")
            elif e > 0 and e < 100:
                observations.append(f"e is small ({e}).")
                
        # 4. Attempt Local Factoring if N is small or vulnerable
        if n and not (p and q):
            # Try Fermat first (good for near-square)
            fermat_res = bounded_factorization.fermat_factorization(n, iter_limit=100_000)
            if fermat_res:
                p, q = fermat_res
                parameters["p"], parameters["q"] = p, q
                observations.append("Successfully factored n using Fermat's Factorization (p and q were close)!")
                # Recalculate D
                if e:
                    try:
                        phi = euler_phi(p, q)
                        d = mod_inverse(e, phi)
                        parameters["d"] = d
                        observations.append("Calculated d following successful Fermat factorization.")
                    except ValueError:
                        pass
            else:
                # Try Trial Division
                trial_res = bounded_factorization.trial_division(n, time_limit=1.5)
                if trial_res:
                    p, q = trial_res
                    parameters["p"], parameters["q"] = p, q
                    observations.append("Successfully factored n using Trial Division (n had small factors)!")
                    if e:
                        try:
                            phi = euler_phi(p, q)
                            d = mod_inverse(e, phi)
                            parameters["d"] = d
                            observations.append("Calculated d following successful Trial Division.")
                        except ValueError:
                            pass
                            
        # 5. Check if we can decrypt
        plaintext = None
        if c and d and n:
            try:
                # c^d mod n
                pt_int = pow(c, d, n)
                parameters["pt_int"] = pt_int
                # Try to decode to bytes
                pt_bytes = pt_int.to_bytes((pt_int.bit_length() + 7) // 8, byteorder='big')
                try:
                    plaintext = pt_bytes.decode('utf-8')
                    observations.append(f"Successfully decrypted c to text: {plaintext}")
                except UnicodeDecodeError:
                    plaintext = pt_bytes.hex()
                    observations.append(f"Successfully decrypted c to hex: {plaintext}")
            except Exception as ex:
                observations.append(f"Decryption failed: {ex}")
                
        return CryptoResult(
            algorithm="RSA Assessment",
            operation="analyze",
            success=True,
            plaintext=plaintext,
            parameters=parameters,
            observations=observations,
            execution_time=time.time()-start_time
        )

rsa_assessment_service = RSAAssessmentService()
