class TronDecypherError(Exception):
    """Base exception for all TRON-DeCypher errors."""

class ConfigurationError(TronDecypherError):
    """Raised when there is a configuration error."""

class PluginError(TronDecypherError):
    """Raised when a plugin operation fails."""

