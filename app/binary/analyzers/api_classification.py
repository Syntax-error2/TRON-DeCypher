class APIClassificationService:
    """Classifies imported functions into standard DFIR/CTF observational categories."""
    
    CATEGORIES = {
        "Memory": ["virtualalloc", "virtualprotect", "virtualfree", "heapalloc", "heapcreate", "mmap", "mprotect"],
        "File I/O": ["createfile", "writefile", "readfile", "open", "read", "write", "fopen", "fread", "fwrite"],
        "Process/Thread": ["createprocess", "createremotethread", "openprocess", "execve", "fork", "clone", "system", "winexec"],
        "Networking": ["wsastartup", "socket", "connect", "send", "recv", "urldownloadtofile", "winhttpconnect", "internetopen"],
        "Registry": ["regopenkey", "regcreatekey", "regsetvalue"],
        "Cryptography": ["cryptacquirecontext", "cryptencrypt", "bcryptencrypt", "ssl_read"],
        "Debugging": ["isdebuggerpresent", "checkremotedebuggerpresent", "outputdebugstring", "ptrace"],
        "Persistence": ["createservice", "regsetvalueex"]
    }
    
    def classify(self, function_name: str) -> str:
        if not function_name:
            return "Unknown"
            
        lower_name = function_name.lower()
        for cat, keywords in self.CATEGORIES.items():
            for kw in keywords:
                if kw in lower_name:
                    return cat
                    
        return "Standard"

api_classification_service = APIClassificationService()
