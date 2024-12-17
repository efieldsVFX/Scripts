# Project Management Tools Suite

A sophisticated collection of production pipeline tools designed for efficient project management and task organization in VFX production environments. These tools seamlessly integrate with ftrack for robust project tracking and management.

## Core Components

### Project Setup Tool (`Project_setup.py`)

A powerful GUI-based utility for initializing and configuring new projects with automated project management integration.

![Project Creator Interface](docs/images/ProjectCreator.png)

#### Key Features
- **Project Management Interface**
  - Automated project structure creation
  - Direct ftrack integration
  - Visual configuration interface
- **Thumbnail Management**: Built-in support for project thumbnail handling using PIL
- **Robust Error Handling**: Comprehensive logging and error management system

#### Technical Implementation
- **Framework**: PyQt5 for responsive GUI
- **Project Management API**: ftrack_api for seamless project tracking
- **Image Processing**: PIL (Python Imaging Library) for thumbnail manipulation
- **Configuration**: JSON-based project templates and settings
- **Logging**: Structured logging system for debugging and monitoring

### Task Manager Tool (`task_manager.py`)

An advanced task management system for handling complex task hierarchies and relationships across projects.

#### Key Features
- **Visual Task Management**: Tree-based visualization of project structures
- **Intelligent Task Movement**: Preserves task hierarchies and relationships during transfers
- **Timeline Management**: Automatic date adjustment for task movements
- **Data Integrity**: Robust validation system for task operations
- **Progress Tracking**: Real-time operation progress monitoring

#### Technical Implementation
- **UI Framework**: PyQt5 with QTreeWidget for hierarchy visualization
- **Project Management**: Deep integration with ftrack API
- **Data Validation**: Custom validation system with TaskMoverException handling
- **Structure Preservation**: Recursive algorithms for maintaining task relationships
- **Timeline Handling**: Sophisticated date adjustment algorithms

### Asset Creator (`asset_creator.py`)

An advanced asset management system for creating and organizing production assets across multiple pipeline systems.

#### Key Features
- **Asset Management Interface**
  - Professional dark theme interface
  - Intuitive form layout
  - Smart input controls
  - Asset preview and version tracking

- **Pipeline Integration**
  - Seamless Unreal Engine workflow
  - Prism Pipeline connectivity
  - Multi-pipeline support
  - Project structure standardization

- **Smart Asset Organization**
  - Automated folder structure creation
  - Asset type categorization
  - Version control integration
  - Thumbnail generation

#### Technical Implementation
- **Framework**: PyQt5/PySide2 for GUI
- **Pipeline APIs**: 
  - Unreal Engine integration
  - Prism Pipeline connectivity
  - Version control system hooks
- **Asset Management**: 
  - Standardized naming conventions
  - Automated metadata handling
  - Asset relationship tracking

## Technologies Used

- **Python 3.x**: Core programming language
- **ftrack API**: Project management integration
- **PyQt5**: GUI framework
- **PIL**: Image processing
- **JSON**: Configuration management

## Pipeline Integration

These tools are designed to seamlessly integrate into existing VFX pipelines:

- **Standardized Project Structure**: Ensures consistency across all projects
- **API-First Design**: Easy integration with other pipeline tools
- **Configurable Workflows**: Adaptable to different production requirements
- **Error Recovery**: Robust error handling and logging for production stability

## Use Cases

1. **Project Initialization**
   - Automated setup of new projects with standardized structures
   - Integration with project management systems
   - Configuration of project-specific settings

2. **Task Management**
   - Complex task reorganization across projects
   - Bulk task movements with relationship preservation
   - Timeline management and adjustment

## Technical Details

### Architecture
- **Modular Design**: Separate modules for project setup and task management
- **Event-Driven**: Responsive GUI with real-time updates
- **Data-Centric**: Strong focus on data integrity and validation

### Error Handling
- **Custom Exceptions**: Specialized error handling for different scenarios
- **Logging System**: Comprehensive logging for debugging and monitoring
- **User Feedback**: Clear error messages and status updates

## Future Enhancements

- Integration with additional project management systems
- Extended support for custom project templates
- Advanced task dependency visualization
- Batch operations for multiple projects
- Timeline optimization algorithms

## Performance Considerations

- Efficient handling of large project structures
- Optimized database queries for task management
- Responsive GUI even with complex operations
- Memory-efficient task tree handling

## Developer
Developed by Eric Fields (efieldsvfx@gmail.com)
