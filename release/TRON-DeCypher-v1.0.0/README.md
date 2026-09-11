# TRON-DeCypher

TRON-DeCypher is a professional cybersecurity analysis and CTF/DFIR toolkit, designed for authorized cybersecurity exercises, CTF competitions, cyber-defense training, digital forensics practice, and preparation for the TRON Cyber Exercise 2026 National Championship.

## Intended Use
This project is intended strictly for authorized cyber exercises, labs, and CTF environments. See `docs/SECURITY.md` for our security principles.

## Technology Stack
- **Language**: Python 3.12+
- **Desktop GUI**: PySide6
- **Data**: SQLite
- **Configuration**: Pydantic / pydantic-settings
- **HTTP/API**: httpx
- **Terminal/log output**: Rich
- **Environment variables**: python-dotenv
- **Testing**: pytest
- **Linting/formatting**: Ruff
- **Type checking**: mypy

## Installation
1. Ensure Python 3.12+ is installed.
2. Clone the repository and navigate to the root directory.
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Development Setup
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

## How to Run
```bash
python -m app.main
```

## Project Architecture
See `docs/ARCHITECTURE.md` for a detailed breakdown of the system architecture.

## Testing
Run the test suite using pytest:
```bash
pytest
```

## Current Phase
Phase 1 — Foundation & Architecture Only

## Roadmap
See `docs/ROADMAP.md` for the planned phases of development.
