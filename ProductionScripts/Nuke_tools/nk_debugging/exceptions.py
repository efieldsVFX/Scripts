class NukeDebugError(Exception):
    """Base exception for all debugging tool errors."""
    pass

class ConfigError(NukeDebugError):
    """Configuration related errors."""
    pass

class NodeOperationError(NukeDebugError):
    """Errors during node operations."""
    pass

class LoggingError(NukeDebugError):
    """Errors during logging operations."""
    pass 