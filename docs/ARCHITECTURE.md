# TRON-DeCypher Architecture

The system is designed with a layered architecture to separate concerns, ensure testability, and allow for a rich ecosystem of plugins and tools.

## Current Architecture Flow

```
UI (PySide6)
  ↓
Services (Business Logic)
  ↓
Core (Config, Paths, Logging)
  ↓
Models (Pydantic / Typed Data)
  ↓
Database (SQLite)
```

## Future Architecture Flow (Planned)

```
UI (PySide6)
  ↓
Plugin Manager
  ↓
Analysis / Decoder Plugins
  ↓
Tool Runner
  ↓
Local Tools / Optional APIs
```

- **UI**: Handles user interactions, built with PySide6.
- **Services**: Contains the core business logic (e.g., managing cases, artifacts).
- **Core**: Contains infrastructure code (paths, constants, exceptions, logging).
- **Models**: Defines the data structures using strong typing (Pydantic, dataclasses).
- **Database**: Handles persistence using SQLite.
- **Plugins**: A flexible system to extend the application's capabilities (decoders, analyzers).
