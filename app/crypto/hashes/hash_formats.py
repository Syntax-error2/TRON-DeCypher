class HashFormat:
    def __init__(self, name: str, display_name: str, family: str, digest_length_hex: int | None,
                 charset: str, prefix_patterns: list[str], salt_support: bool,
                 parameter_structure: str | None, security_notes: str,
                 is_structured: bool = False):
        self.name = name
        self.display_name = display_name
        self.family = family
        self.digest_length_hex = digest_length_hex
        self.charset = charset
        self.prefix_patterns = prefix_patterns
        self.salt_support = salt_support
        self.parameter_structure = parameter_structure
        self.security_notes = security_notes
        self.is_structured = is_structured

class HashFormatRegistry:
    def __init__(self) -> None:
        self._formats: dict[str, HashFormat] = {}
        self._register_defaults()

    def register(self, fmt: HashFormat) -> None:
        self._formats[fmt.name] = fmt

    def get_all(self) -> list[HashFormat]:
        return list(self._formats.values())

    def get(self, name: str) -> HashFormat | None:
        return self._formats.get(name)

    def _register_defaults(self) -> None:
        # Standard unsalted hashes
        self.register(HashFormat("md5", "MD5", "MD", 32, "hex", [], False, None, "Cryptographically broken. Local candidate verification possible."))
        self.register(HashFormat("md4", "MD4", "MD", 32, "hex", [], False, None, "Cryptographically broken. Local candidate verification possible."))
        self.register(HashFormat("sha1", "SHA-1", "SHA", 40, "hex", [], False, None, "Cryptographically broken. Local candidate verification possible."))
        self.register(HashFormat("sha224", "SHA-224", "SHA-2", 56, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha256", "SHA-256", "SHA-2", 64, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha384", "SHA-384", "SHA-384", 96, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha512", "SHA-512", "SHA-2", 128, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha512-224", "SHA-512/224", "SHA-2", 56, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha512-256", "SHA-512/256", "SHA-2", 64, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha3-224", "SHA3-224", "SHA-3", 56, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha3-256", "SHA3-256", "SHA-3", 64, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha3-384", "SHA3-384", "SHA-3", 96, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("sha3-512", "SHA3-512", "SHA-3", 128, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("blake2b", "BLAKE2b", "BLAKE", 128, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("blake2s", "BLAKE2s", "BLAKE", 64, "hex", [], False, None, "Secure. Local candidate verification possible."))
        self.register(HashFormat("ripemd160", "RIPEMD-160", "RIPEMD", 40, "hex", [], False, None, "Local candidate verification possible."))
        
        # Windows hashes
        self.register(HashFormat("ntlm", "NTLM", "Windows", 32, "hex", [], False, None, "No salt. Fast to crack."))
        self.register(HashFormat("lm", "LM", "Windows", 32, "hex", [], False, None, "No salt, uppercase only. Extremely fast to crack."))

        # Structured / Salted
        self.register(HashFormat("bcrypt", "bcrypt", "Password", None, "b64", ["$2b$", "$2y$", "$2a$"], True, "Cost, Salt, Hash", "Secure, intentionally slow.", is_structured=True))
        self.register(HashFormat("argon2", "Argon2", "Password", None, "b64", ["$argon2i$", "$argon2d$", "$argon2id$"], True, "Version, Memory, Iterations, Parallelism, Salt, Hash", "State of the art password hash.", is_structured=True))
        self.register(HashFormat("sha512crypt", "SHA512-Crypt", "Unix", None, "b64", ["$6$"], True, "Salt, Hash", "Standard Unix hash.", is_structured=True))
        self.register(HashFormat("sha256crypt", "SHA256-Crypt", "Unix", None, "b64", ["$5$"], True, "Salt, Hash", "Standard Unix hash.", is_structured=True))
        self.register(HashFormat("md5crypt", "MD5-Crypt", "Unix", None, "b64", ["$1$"], True, "Salt, Hash", "Older Unix hash.", is_structured=True))
        self.register(HashFormat("scrypt", "scrypt", "Password", None, "b64", ["$scrypt$", "$7$"], True, "Cost, Block size, Parallelization, Salt, Hash", "Secure, memory-hard.", is_structured=True))
        self.register(HashFormat("pbkdf2", "PBKDF2", "Password", None, "b64", ["$pbkdf2$", "$p5k2$"], True, "Iterations, Salt, Hash", "Secure key derivation.", is_structured=True))
        self.register(HashFormat("phpass", "phpass", "Password", None, "b64", ["$P$", "$H$"], True, "Salt, Hash", "WordPress/PHP hash.", is_structured=True))

hash_format_registry = HashFormatRegistry()
