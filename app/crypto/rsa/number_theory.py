def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean Algorithm. Returns (gcd, x, y) such that a*x + b*y = gcd."""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def gcd(a: int, b: int) -> int:
    """Greatest Common Divisor."""
    g, _, _ = egcd(a, b)
    return g

def mod_inverse(a: int, m: int) -> int:
    """Modular multiplicative inverse. Returns x such that (a * x) % m == 1."""
    g, x, _y = egcd(a, m)
    if g != 1:
        raise ValueError(f"Modular inverse does not exist for a={a}, m={m} (gcd is {g})")
    else:
        return x % m

def euler_phi(p: int, q: int) -> int:
    """Computes Euler's totient function phi(n) for n = p*q where p and q are primes."""
    return (p - 1) * (q - 1)

def isqrt(n: int) -> int:
    """Integer square root."""
    import math
    return math.isqrt(n)
