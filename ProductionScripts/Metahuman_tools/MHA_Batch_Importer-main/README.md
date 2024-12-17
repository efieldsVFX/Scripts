# MetaHuman Automation (MHA) Batch Importer

![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.1+-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A high-performance, production-grade automation tool for batch processing MetaHuman assets in Unreal Engine. This pipeline tool streamlines the integration of MetaHuman face and body animations into your Unreal Engine projects, featuring robust error handling, progress tracking, and seamless FTrack integration.

## Key Features

### Core Functionality
- **Dual Processing Pipelines**
  - Face Animation Import & Processing
  - Body Animation Import & Processing
  - Parallel Processing Support

### Technical Integration
- **Unreal Engine Integration**
  - Direct API Integration via Python
  - Custom Asset Registry Management
  - Automated Import Settings Configuration
  - Real-time Progress Monitoring

### Pipeline Features
- **Asset Management**
  - FTrack Integration with Custom Attributes
  - Automated Asset Organization
  - Batch Processing with Error Recovery
  - Configurable Asset Naming Conventions

### UI/UX
- **Modern Qt-based Interface**
  - Real-time Progress Tracking
  - Detailed Processing Logs
  - Interactive Asset Selection
  - Error Visualization and Reporting

## Technical Architecture

### Core Components
```
MHA_Batch_Importer/
├── processing/
│   ├── face/          # Face animation processing
│   ├── body/          # Body animation processing
│   └── base/          # Shared processing logic
├── gui/               # Qt-based UI components
├── integrations/      # External system integrations
└── config/           # Configuration management
```

### Integration Points
- **Unreal Engine**
  - Asset Registry API
  - Import Settings Management
  - Animation Data Processing
  - Custom Attribute Handling

- **FTrack**
  - Custom Attribute Mapping
  - Asset Status Tracking
  - Pipeline Integration
  - Metadata Management

## Implementation Details

### Face Processing Pipeline
```python
# Key processing steps
1. Asset Discovery & Validation
2. Metadata Extraction & Mapping
3. Import Settings Configuration
4. Processing Queue Management
5. Error Handling & Recovery
```

### Body Processing Pipeline
```python
# Processing workflow
1. FBX Import Configuration
2. Skeletal Mesh Mapping
3. Animation Data Processing
4. Asset Organization
5. Quality Validation
```

## Technical Requirements

### Software Dependencies
- Unreal Engine 5.1+
- Python 3.7+
- PySide6 for UI
- FTrack Python SDK

### Development Environment
```bash
# Install core dependencies
pip install -e .[dev]

# Install development tools
pip install pre-commit black flake8 pytest
```

## Pipeline Integration

### FTrack Setup
```python
# Required Custom Attributes
{
    'actor_names': 'Text',
    'mhid_path': 'Text',
    'skeletal_mesh_path': 'Text'
}
```

### Environment Configuration
```bash
# Core Settings
FTRACK_SERVER="your_server"
FTRACK_API_KEY="your_key"
FTRACK_API_USER="your_user"
FTRACK_PROJECT_ID="your_project"

# Optional Settings
MHA_DEBUG_MODE="True"
MHA_PARALLEL_PROCESSING="True"
```

## Quality Assurance

### Automated Testing
```bash
# Run test suite
pytest

# Style checks
flake8 .
black .
isort .
```

### Error Handling
- Comprehensive error capture and logging
- Automated error recovery mechanisms
- Detailed error reporting in UI
- Pipeline status notifications

## Performance Optimization

### Processing Optimization
- Parallel processing support
- Efficient asset discovery
- Optimized import settings
- Memory management

### UI Performance
- Asynchronous updates
- Efficient progress tracking
- Responsive user interface
- Real-time status updates

## Usage Examples

### Python Console
```python
import mha_batch_importer
mha_batch_importer.run()
```

### Editor Utility Widget
```python
# Add to clicked event
import mha_batch_importer
mha_batch_importer.run()
```

## Security Considerations

- Secure credential management
- Access control integration
- Data validation and sanitization
- Error message sanitization

## Documentation

For detailed documentation on implementation, customization, and troubleshooting, please refer to the inline code documentation.

## Authors

- Eric Fields (efieldsvfx@gmail.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.