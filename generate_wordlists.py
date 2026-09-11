import os

os.makedirs('app/knowledge/dictionaries', exist_ok=True)
os.makedirs('app/knowledge/patterns', exist_ok=True)
os.makedirs('app/knowledge/formats', exist_ok=True)
os.makedirs('app/knowledge/hints', exist_ok=True)
os.makedirs('app/knowledge/categories', exist_ok=True)

roots = [
    "cyber", "security", "defense", "defence", "infosec", "ctf", "capture", "flag", 
    "tron", "troncup", "tronctf", "exercise", "army", "command", "signal",
    "philippines", "philippine", "pinoy", "manila", "luzon", "visayas", "mindanao", "negros",
    "crypto", "forensics", "stego", "network", "web", "binary", "memory", "malware", "osint", "misc",
    "admin", "root", "guest", "user", "administrator", "sysadmin",
    "password", "secret", "hidden", "clue", "hint", "key", "token", "credential",
    "payload", "artifact", "evidence", "shell", "console", "debug", "exploit", "vulnerability",
    "cipher", "decode", "decrypt", "encode", "hash", "digest", "entropy",
    "packet", "stream", "query", "request", "response", "header", "cookie", "session",
    "reverse", "assembly", "process", "dump", "registry", "offset", "signature",
    "md5", "sha1", "sha256", "sha512", "rsa", "aes", "xor", "caesar", "rot13", "rot47", "vigenere", "atbash", "morse", "hex", "base64", "base32", "base58", "base85", "plaintext", "ciphertext", "iv", "nonce", "salt", "checksum",
    "png", "jpg", "jpeg", "gif", "bmp", "zip", "gzip", "pdf", "elf", "pe", "mz", "pcap", "pcapng", "magic", "footer", "overlay", "carve", "carving", "metadata", "exif", "strings", "embedded",
    "tcp", "udp", "dns", "http", "https", "ftp", "smtp", "imap", "pop3", "tls", "ssl", "icmp", "arp", "dhcp", "flow", "socket", "port", "host", "domain", "subdomain", "answer", "proxy", "router", "gateway", "firewall",
    "login", "logout", "dashboard", "api", "api_key", "jwt", "auth", "authorization", "username", "upload", "download", "test", "dev", "staging", "backup", "config", "robots", "sitemap",
    "dll", "so", "mach", "asm", "x86", "x64", "arm", "arm64", "register", "stack", "heap", "pointer", "rva", "section", "import", "export", "symbol", "entry", "entrypoint", "shellcode", "loader", "packer", "unpack", "obfuscation",
    "lsb", "bit", "bitplane", "channel", "rgb", "rgba", "alpha", "pixel", "steganography", "image", "palette", "noise",
    "pid", "ppid", "module", "handle", "commandline", "powershell", "cmd", "volatility", "injection", "hollowing", "thread", "environment",
    "trojan", "ransomware", "dropper", "c2", "control", "persistence", "service", "scheduled", "task", "inject", "execute", "mutex", "yara", "capa",
    "hello", "world", "qwerty", "123456", "letmein", "changeme", "password123"
]

years = ["2024", "2025", "2026", "2027", "26", "27"]
prefixes = ["tron", "ctf", "cyber", "super", "my", "the"]
suffixes = ["ctf", "cup", "2026", "admin", "root", "key", "flag"]

words = set(roots)

# Generate combinations to reach >5000
for root in roots:
    for year in years:
        words.add(root + year)
        words.add(root + "_" + year)
        words.add(root + "-" + year)
    for pre in prefixes:
        words.add(pre + root)
        words.add(pre + "_" + root)
    for suf in suffixes:
        words.add(root + suf)
        words.add(root + "_" + suf)
        
    # capitalize
    words.add(root.capitalize())
    words.add(root.upper())

master_list = sorted(list(words))
print(f"Generated {len(master_list)} unique words")

with open('app/knowledge/dictionaries/tron_ctf_master.txt', 'w', encoding='utf-8') as f:
    for w in master_list:
        f.write(w + '\n')

def save_subset(filename, keywords):
    subset = set()
    for w in master_list:
        for k in keywords:
            if k in w.lower():
                subset.add(w)
    with open(f'app/knowledge/dictionaries/{filename}', 'w', encoding='utf-8') as f:
        for w in sorted(list(subset)):
            f.write(w + '\n')

save_subset('ctf_crypto.txt', ['crypto', 'md5', 'sha', 'aes', 'rsa', 'cipher', 'hash'])
save_subset('ctf_forensics.txt', ['forensic', 'png', 'exif', 'carve', 'artifact'])
save_subset('ctf_network.txt', ['network', 'pcap', 'tcp', 'udp', 'http', 'dns', 'packet'])
save_subset('ctf_web.txt', ['web', 'admin', 'login', 'cookie', 'session', 'jwt', 'auth'])
save_subset('ctf_binary.txt', ['binary', 'elf', 'pe', 'asm', 'stack', 'heap', 'shellcode'])
save_subset('ctf_stego.txt', ['stego', 'lsb', 'bitplane', 'rgb', 'pixel'])
save_subset('ctf_memory.txt', ['memory', 'pid', 'dump', 'volatility', 'process'])
save_subset('ctf_malware.txt', ['malware', 'trojan', 'c2', 'ransomware', 'yara'])
save_subset('ctf_osint.txt', ['osint', 'domain', 'subdomain', 'host'])
save_subset('ctf_tron_context.txt', ['tron', 'cyber', 'philippine', 'manila'])

with open('app/knowledge/dictionaries/README.md', 'w', encoding='utf-8') as f:
    f.write("# TRON-DeCypher Training Wordlists\n\nThese wordlists are intended for CTF and cybersecurity training. They contain generic terms and combinations. **They do not contain official challenge answers or secrets.**\n")

