import hashlib

from app.knowledge.knowledge_service import knowledge_service


def seed_knowledge_base() -> None:
    # Check if already seeded
    res = knowledge_service.search("Caesar")
    if len(res) > 0:
        return # Already seeded
        
    source1_title = "Getting Started with CTF Challenges"
    source1_sha = hashlib.sha256(source1_title.encode()).hexdigest()
    doc1 = knowledge_service.register_document(
        title=source1_title, 
        filename="Getting_Started_CTF.pdf", 
        sha256=source1_sha, 
        source_type="USER_REFERENCE"
    )
    
    source2_title = "CTF Master Cheatsheet"
    source2_sha = hashlib.sha256(source2_title.encode()).hexdigest()
    doc2 = knowledge_service.register_document(
        title=source2_title, 
        filename="Ctf-CheatSheet-2.pdf", 
        sha256=source2_sha, 
        source_type="USER_CHEATSHEET"
    )

    # Add sections and chunks for Source 1
    # CRYPTO
    sec1_crypto = knowledge_service.add_section(doc1, 15, "Cryptography", "Crypto", "Cryptography basics and common ciphers.")
    knowledge_service.add_chunk(doc1, sec1_crypto, "Caesar Cipher", "A substitution cipher where each letter is replaced by a letter some fixed number of positions down the alphabet.", "caesar, shift, substitution", "", "", "Substitution")
    knowledge_service.add_chunk(doc1, sec1_crypto, "RSA", "Public-key cryptosystem. Look for small e, common moduli, weak primes, Fermat factorization.", "rsa, p, q, n, e, d", "", "", "Fermat factorization, Wiener's attack")
    knowledge_service.add_chunk(doc1, sec1_crypto, "AES", "Advanced Encryption Standard. Common flaws include improper padding (Padding Oracle), weak keys, ECB mode.", "aes, block cipher, ecb, padding", "", "", "Padding Oracle, Block analysis")
    
    # WEB
    sec1_web = knowledge_service.add_section(doc1, 10, "Web Exploitation", "Web", "Web exploitation fundamentals.")
    knowledge_service.add_chunk(doc1, sec1_web, "SQL Injection", "Injecting malicious SQL queries to manipulate backend databases.", "sqli, sql injection", "sqlmap", "", "Error-based, Union-based, Blind")
    knowledge_service.add_chunk(doc1, sec1_web, "XSS", "Cross-Site Scripting. Injecting scripts into web pages viewed by others.", "xss, javascript", "", "", "Reflected, Stored, DOM")
    knowledge_service.add_chunk(doc1, sec1_web, "Directory Traversal / LFI", "Accessing files outside the intended web root.", "lfi, directory traversal, /etc/passwd", "", "", "Dot-dot-slash")
    
    # REVERSE ENGINEERING
    sec1_rev = knowledge_service.add_section(doc1, 25, "Reverse Engineering", "Reverse", "Analyzing compiled binaries.")
    knowledge_service.add_chunk(doc1, sec1_rev, "Disassembly & Decompilation", "Use tools like Ghidra or IDA Free to convert machine code to assembly or C-like pseudocode. Look for strings and label functions.", "ghidra, ida, disassembly, decompilation, strings", "Ghidra, IDA Free, GDB", "", "Static analysis, Dynamic debugging")
    
    # PWN
    sec1_pwn = knowledge_service.add_section(doc1, 35, "Pwn / Binary Exploitation", "Pwn", "Exploiting memory corruption.")
    knowledge_service.add_chunk(doc1, sec1_pwn, "Buffer Overflow", "Overwriting memory adjacent to a buffer. Often leads to taking control of the instruction pointer.", "buffer overflow, bof, segfault", "GDB, Pwntools, checksec", "", "ROP, Shellcode")
    knowledge_service.add_chunk(doc1, sec1_pwn, "Format String", "Exploiting printf-style functions to read/write arbitrary memory.", "format string, %x, %n", "", "", "Arbitrary read/write")
    
    # FORENSICS
    sec1_for = knowledge_service.add_section(doc1, 45, "Forensics", "Forensics", "Digital forensics and incident response.")
    knowledge_service.add_chunk(doc1, sec1_for, "File Type Detection & Metadata", "Don't trust extensions. Use 'file', examine headers, and extract metadata with ExifTool.", "magic bytes, headers, metadata", "file, ExifTool, xxd", "", "Header analysis")
    knowledge_service.add_chunk(doc1, sec1_for, "Memory Analysis", "Analyzing RAM dumps to extract processes, keys, and history.", "memory, ram dump, vmem", "Volatility", "", "Process extraction")
    knowledge_service.add_chunk(doc1, sec1_for, "Network Forensics", "Analyzing PCAP files for credentials or hidden streams.", "pcap, network, packets", "Wireshark", "", "Stream following, Object extraction")
    
    # Source 2: Tools and Commands
    sec2_stego = knowledge_service.add_section(doc2, 12, "Audio / Steganography", "Stego", "Hiding data in media.")
    knowledge_service.add_chunk(doc2, sec2_stego, "Steganography", "Hiding data in LSB (Least Significant Bit), bitplanes, or appended to files.", "stego, lsb, bitplane, hidden data", "zsteg, JSteg, binwalk, pngcheck", "", "LSB extraction, Carving")
    knowledge_service.add_chunk(doc2, sec2_stego, "Audio Analysis", "Hidden messages in audio frequencies (spectrogram) or DTMF tones.", "audio, spectrogram, dtmf, morse", "Audacity, Sonic Visualiser, multimon-ng", "", "Spectrogram viewing")
    
    sec2_archive = knowledge_service.add_section(doc2, 20, "Archive / File Cracking", "Archive", "Cracking passwords on ZIP, PDF, etc.")
    knowledge_service.add_chunk(doc2, sec2_archive, "Archive Cracking", "Brute-forcing or dictionary attacking encrypted archives.", "zip, pdf, password, crack", "John the Ripper, fcrackzip, pdfcrack, zipinfo, zipdetails", "", "Dictionary attack")
    
    sec2_osint = knowledge_service.add_section(doc2, 22, "OSINT", "OSINT", "Open Source Intelligence.")
    knowledge_service.add_chunk(doc2, sec2_osint, "Search & Discovery", "Using Google Dorks (site:, inurl:, intitle:, filetype:) and image metadata to find hidden info.", "osint, google dorks, exif", "ExifTool", "", "Dorking")
    
    sec2_net = knowledge_service.add_section(doc2, 25, "Networking", "Network", "Network enumeration and interaction.")
    knowledge_service.add_chunk(doc2, sec2_net, "Enumeration & Connect", "Scanning ports and interacting with services.", "port scan, banner grab, tcp, udp", "Nmap, Netcat", "", "Port scanning")
    
    sec2_web = knowledge_service.add_section(doc2, 5, "Web Exploitation", "Web", "Web cheatsheet.")
    knowledge_service.add_chunk(doc2, sec2_web, "Directory Fuzzing", "Finding hidden directories and files.", "fuzz, gobuster, dirb", "ffuf, Burp Suite, OWASP ZAP", "", "Fuzzing")
    
    sec2_misc = knowledge_service.add_section(doc2, 30, "Miscellaneous", "Misc", "Misc encodings and utilities.")
    knowledge_service.add_chunk(doc2, sec2_misc, "Encoding/Decoding", "Converting data formats (Base64, Hex, etc).", "base64, hex, encoding", "xxd, base64", "", "Decoding")

    # Add Tools
    knowledge_service.add_tool("Ghidra", "Reverse", "Decompile/inspect binaries", source1_title, 25)
    knowledge_service.add_tool("Wireshark", "Network", "Network packet analysis", source1_title, 45)
    knowledge_service.add_tool("Volatility", "Forensics", "Memory analysis", source1_title, 45)
    knowledge_service.add_tool("ExifTool", "Forensics", "Metadata extraction", source1_title, 45)
    knowledge_service.add_tool("zsteg", "Stego", "Detect hidden LSB data in PNG/BMP", source2_title, 12)
    knowledge_service.add_tool("ffuf", "Web", "Fast web fuzzer", source2_title, 5)
    knowledge_service.add_tool("sqlmap", "Web", "Automated SQL injection", source2_title, 5)

    # Add Commands
    knowledge_service.add_command("nmap", "nmap -sV -sC -p- <ip>", "Scan all ports with version detection and default scripts.", "Network", source2_title, 25)
    knowledge_service.add_command("netcat", "nc -lvnp 4444", "Listen for incoming reverse shells.", "Network", source2_title, 25)
    knowledge_service.add_command("sqlmap", "sqlmap -u '<url>' --dbs", "Enumerate databases.", "Web", source2_title, 5)
    knowledge_service.add_command("ffuf", "ffuf -w wordlist.txt -u http://<url>/FUZZ", "Fuzz directories.", "Web", source2_title, 5)
    knowledge_service.add_command("gdb", "gdb ./binary", "Start GDB.", "Pwn", source2_title, 15)

    # Add Workflows
    knowledge_service.add_workflow("Forensics", "Forensics Quick Triage", 
                                  "1. Identify file type\n2. Inspect headers\n3. Inspect metadata\n4. Check for hidden data\n5. Consider carving\n6. Check steganography\n7. Analyze PCAP/memory where applicable", 
                                  source1_title)

if __name__ == "__main__":
    seed_knowledge_base()
    print("Database seeded with CTF knowledge.")
