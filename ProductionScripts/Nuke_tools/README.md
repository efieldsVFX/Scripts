# Nuke Production Tools

A comprehensive suite of tools for Nuke compositing workflow optimization and debugging. Last Updated: December 19, 2024

## Tools Overview

### Node Validator (`NK_Node_Validator.py`)
Advanced node validation and optimization system featuring:
- Automated node graph analysis
- Batch processing capabilities
- Backup management
- Progress tracking
- Custom validation rules
- Results export functionality

### UI Fix Tool (`NK_UI_fix.py`)
Interface optimization and repair utility providing:
- UI element restoration
- Layout fixes
- Custom panel management
- Interface state preservation

### Debugging Suite (`nk_debugging/`)
Professional-grade debugging toolkit including:
- Performance optimization
- Thread management
- Memory allocation control
- Node state management
- System analysis
- Qt-based debug interface

## Features

### Performance Optimization
- Multi-threaded batch processing
- Memory usage optimization
- Cache management
- System resource monitoring

### Safety and Reliability
- Automatic backups
- Undo context management
- Error logging and tracking
- State preservation

### User Interface
- Modern Qt-based interfaces
- Progress tracking
- Interactive controls
- Status reporting

## Installation

1. Copy the tools to your Nuke plugins directory
2. Add to your `init.py`:
```python
nuke.pluginAddPath("./Nuke_tools")
```

## Requirements
- Nuke 13.0+
- Python 3.7+
- PySide2
- PyYAML (for configuration)

## Usage Examples

### Node Validator
```python
import NK_Node_Validator
NK_Node_Validator.run_validation()
```

### Debug Tools
```python
from nk_debugging.views import DebugPanel
panel = DebugPanel()
panel.show()
```

## Configuration

Each tool maintains its own configuration file:
- `validator_config.yaml` for Node Validator
- `debug_config.yaml` for Debugging Suite

## Support

For issues, feature requests, or general support, contact the pipeline team.

## License

Internal use only - All rights reserved.