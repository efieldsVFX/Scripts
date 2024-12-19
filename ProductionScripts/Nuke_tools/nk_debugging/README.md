# Nuke Debugging Tools

A comprehensive debugging toolkit for Nuke compositing software. Last Updated: December 19, 2024

## Overview

This package provides a robust set of debugging tools for Nuke, featuring a modern Qt-based interface and extensive system analysis capabilities.

## Components

### Core Modules

- **controllers.py**: Core debugging logic implementation
  - Thread management
  - Memory allocator control
  - Node enabling/disabling
  - Media localization
  - System state management

- **views.py**: Qt-based user interface
  - Progress tracking dialogs
  - Debug panel interface
  - Status reporting
  - Interactive controls

- **models.py**: Data structures and state management
  - System information tracking
  - Debug state preservation
  - Configuration models

- **utils.py**: Utility functions
  - Undo context management
  - Node operations
  - System information gathering

### Support Modules

- **config.py**: Configuration management
  - Debug settings
  - User preferences
  - System defaults

- **constants.py**: System constants
  - Debug actions
  - State definitions
  - Default values

- **logger.py**: Logging system
  - Debug logging
  - Error tracking
  - Operation history

- **exceptions.py**: Custom exceptions
  - Error handling
  - Debug-specific exceptions

## Features

### Performance Debugging
- Thread count management
- Memory allocator optimization
- System resource monitoring
- Performance bottleneck detection

### Node Management
- Selective node disabling
- Class-based node operations
- Node state preservation
- Batch operations support

### Media Handling
- Localization policy control
- Cache management
- File path verification
- Read node optimization

### System Analysis
- Resource usage tracking
- Configuration validation
- Error state detection
- System health reporting

## Usage

```python
from nk_debugging.controllers import DebugController
from nk_debugging.views import DebugPanel

# Create and show debug panel
panel = DebugPanel()
panel.show()

# Or use controller directly
controller = DebugController()
controller.limit_threads(4)
controller.change_allocator("malloc")
```

## Requirements
- Nuke 13.0+
- PySide2
- Python 3.7+

## Installation

1. Copy the `nk_debugging` directory to your Nuke plugins directory
2. Add to your `init.py`:
```python
nuke.pluginAddPath("./nk_debugging")
```

## Error Handling

The toolkit provides comprehensive error handling through custom exceptions and logging:
- All operations are wrapped in undo contexts
- Detailed error logging
- User-friendly error messages
- State preservation on failure

## Support

For bug reports or feature requests, contact the pipeline team.