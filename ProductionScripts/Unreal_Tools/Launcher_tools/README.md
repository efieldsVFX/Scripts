# Unreal Engine Launcher Tools

A sophisticated project launcher and environment management system for Unreal Engine. Last Updated: December 19, 2024

## 🎮 Features

### Project Management
- **Project Selection**
  - Dynamic project discovery
  - Recent projects tracking
  - Custom project paths
  - Project validation

### Environment Control
- **Engine Version Management**
  - Multiple engine version support
  - Environment variable handling
  - Path validation and setup
  - Configuration persistence

### Build System
- **Build Configuration**
  - Custom build settings
  - Platform-specific options
  - Build validation
  - Error handling

### User Interface
- **Qt-based Interface**
  - Modern dark theme
  - Project status indicators
  - Progress tracking
  - Error notifications

## 🔧 Technical Details

### Dependencies
- Python 3.7+
- PyQt5
- Unreal Engine 5.4+

### Configuration
- Settings stored in QSettings
- Project paths configuration
- Engine version management
- Build system setup

## 🚀 Usage

```python
from Launcher_tools import launcher

# Create launcher instance
launcher_app = launcher.UnrealEngineLauncher()
launcher_app.show()
```

## 📝 License
Internal use only - All rights reserved.

## Author
**Eric Fields** - Pipeline Technical Director  
Contact: [efieldsvfx@gmail.com](mailto:efieldsvfx@gmail.com)
