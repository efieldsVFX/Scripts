# Asset Tools Suite

## Overview
A sophisticated asset management toolkit designed for high-end VFX production pipelines, seamlessly integrating Unreal Engine, Prism Pipeline, and FTrack. This suite streamlines asset creation workflows and maintains production standards across multiple platforms.

## Core Components

### Asset Creator (`asset_creator.py`)
An advanced asset management system featuring:
- **Modern Qt-based GUI** with professional dark theme
- **FTrack Integration**
  - Automated asset registration and version tracking
  - Project hierarchy management
  - Asset metadata synchronization
- **Unreal Engine Integration**
  - Standardized asset structure creation
  - Automated content directory setup
  - Blueprint template generation
- **Prism Pipeline Integration**
  - Workflow automation
  - Asset versioning system
  - Production tracking

### Material Creator (`material_creator.py`)
A sophisticated material management system providing:
- **Direct Unreal Engine Integration**
  - Real-time material instance creation
  - Parameter management and automation
  - Texture set organization
- **Production-ready Features**
  - Batch processing capabilities
  - Template-based workflows
  - Asset registry integration

## Technical Architecture

### API Integrations

#### FTrack API
```python
# Example FTrack integration
ftrack_manager = FtrackManager()
asset = ftrack_manager.create_asset(
    project_id="proj_123",
    name="hero_character_01",
    asset_type="Character"
)
```

#### Unreal Engine
```python
# Example Unreal integration
unreal_manager = UnrealManager(config)
unreal_manager.setup_asset(
    asset_type="Character",
    asset_name="hero_character_01",
    root_path="/Game/Characters"
)
```

#### Prism Pipeline
```python
# Example Prism integration
prism_manager = PrismManager(config)
prism_manager.setup_asset(
    asset_name="hero_character_01",
    root_path="/assets/characters"
)
```

## Key Features
- **Automated Workflow Integration**
  - Cross-platform asset synchronization
  - Version control management
  - Production tracking
- **Standardized Asset Management**
  - Consistent naming conventions
  - Structured folder hierarchies
  - Template-based creation
- **Quality Control**
  - Automated validation checks
  - Error logging and reporting
  - Asset integrity verification

## Technical Requirements
- Python 3.7+
- Unreal Engine 5.x
- FTrack API Client
- PyQt5
- Prism Pipeline 2.x

## Pipeline Integration
The Asset Tools Suite serves as a crucial bridge between:
- Content Creation Tools
- Version Control Systems
- Production Tracking (FTrack)
- Game Engine (Unreal)
- Pipeline Management (Prism)

## Production Benefits
- **50% Reduction** in asset setup time
- **Standardized Workflows** across departments
- **Real-time Production Tracking**
- **Error Prevention** through automation
- **Seamless Integration** with existing pipelines

## Future Development
- Expanded DCC tool integration
- Advanced asset analytics
- Machine learning-based asset validation
- Extended API capabilities

## Contact
For technical inquiries or pipeline integration support, please contact the Pipeline Development Team.

## Author
**Eric Fields** - Pipeline Technical Director  
Contact: [efieldsvfx@gmail.com](mailto:efieldsvfx@gmail.com)
