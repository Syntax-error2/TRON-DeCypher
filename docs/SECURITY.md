# Security Principles

TRON-DeCypher is intended for authorized cyber exercises, labs, and CTF environments. The following security principles must be strictly followed during development:

1. **Safe Execution**: Imported challenge artifacts must never be blindly executed.
2. **Subprocess Handling**: Use safe subprocess handling for all external tools. Avoid `shell=True` unless strictly necessary and sanitized.
3. **Controlled Execution**: External tools must be executed in a controlled manner with appropriate timeouts and resource limits.
4. **Path Traversal Protection**: All file paths and user inputs must be validated to prevent path traversal attacks.
5. **Input Validation**: All inputs, whether from users, files, or external APIs, must be validated.
6. **Secrets Protection**: API keys, passwords, and tokens must never be hardcoded or logged. Use `.env` files and environment variables.
7. **Audit Logging**: Important actions and state changes should be securely logged.
8. **Network Access**: Network access should be optional and controllable by the user.
9. **Explicit Confirmation**: Potentially dangerous actions must require explicit user confirmation.
10. **No Autonomous Attacks**: The system must not perform autonomous attacks against arbitrary external systems.
