# Maya Production Tools

A collection of professional Maya automation tools designed to streamline production workflows and maintain scene integrity. Last Updated: December 19, 2024

## Tools Overview

### 1. Maya Scene Cleanup (`Maya_Cleanup.py`)
A comprehensive scene cleanup utility with a user-friendly Qt interface for optimizing Maya scenes.

#### Features:
- **Scene Element Cleanup**
  - Remove unused materials and textures
  - Clean up audio nodes
  - Delete unknown plugins
  - Manage render layers

- **Safety Features**
  - Automatic scene backup before operations
  - Protected node preservation
  - Preview changes before execution
  - Comprehensive logging

- **User Interface**
  - Modern Qt-based interface
  - Progress tracking
  - Operation previews
  - Status updates

### 2. Frame Range Manager (`Maya_FrameRange.py`)
An automated frame range synchronization tool integrated with ShotGrid pipeline.

#### Features:
- **ShotGrid Integration**
  - Automatic frame range retrieval
  - Version compatibility checking
  - Pipeline integration

- **Safety and Logging**
  - Comprehensive error handling
  - Detailed logging system
  - Non-blocking user notifications

- **Workflow Support**
  - Batch mode support
  - Standalone operation capability
  - Pipeline-aware functionality

## Installation

1. Copy the tools to your Maya scripts directory
2. Add the following to your Maya.env file:
   ```
   PYTHONPATH = path/to/tools/directory;$PYTHONPATH
   ```

## Usage

### Scene Cleanup Tool
```python
import Maya_Cleanup
Maya_Cleanup.main()
```

### Frame Range Manager
```python
import Maya_FrameRange
Maya_FrameRange.load_new_framerange()
```

## Requirements
- Maya 2020 or later
- Python 3.7+
- PySide2
- ShotGrid Toolkit (for Frame Range Manager)

## Configuration

### Scene Cleanup
The tool uses a configuration file (`render_cleaner_config.json`) to store:
- Protected node lists
- Backup preferences
- Logging settings

### Frame Range Manager
Requires proper ShotGrid pipeline setup with:
- Valid SGTK configuration
- Proper environment variables
- Project-specific settings

## Logging
Both tools maintain detailed logs:
- Scene Cleanup: `cleanup_log_[timestamp].txt`
- Frame Range: `maya_framerange.log`

## Support
For issues or feature requests, please contact the pipeline team.

## License
Internal use only - All rights reserved.