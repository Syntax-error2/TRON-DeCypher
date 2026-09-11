import time

from app.crypto.rsa.number_theory import isqrt


class BoundedFactorization:
    """Bounded local mathematical factorization utilities for CTF."""
    
    def trial_division(self, n: int, time_limit: float = 2.0) -> tuple[int, int] | None:
        """Attempts to factor n via trial division within a time limit."""
        if n % 2 == 0:
            return 2, n // 2
            
        start_time = time.time()
        
        # We only go up to a reasonable limit bound by time
        limit = min(isqrt(n) + 1, 10_000_000)
        
        for i in range(3, limit, 2):
            if time.time() - start_time > time_limit:
                break
            if n % i == 0:
                return i, n // i
                
        return None

    def fermat_factorization(self, n: int, iter_limit: int = 1_000_000) -> tuple[int, int] | None:
        """
        Fermat's factorization method. Effective when p and q are close to each other.
        n = a^2 - b^2 = (a-b)(a+b)
        """
        if n % 2 == 0:
            return 2, n // 2
            
        a = isqrt(n)
        if a * a == n:
            return a, a
            
        a += 1
        b2 = a * a - n
        
        iterations = 0
        while iterations < iter_limit:
            b = isqrt(b2)
            if b * b == b2:
                return a - b, a + b
            a += 1
            b2 = a * a - n
            iterations += 1
            
        return None

bounded_factorization = BoundedFactorization()
