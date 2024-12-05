# MHA Batch Importer

A production-ready tool for batch importing MetaHuman assets into Unreal Engine with FTrack integration. This tool streamlines the process of importing and managing MetaHuman assets in your Unreal Engine project.

## Features

- Batch import of MetaHuman assets
- FTrack integration for asset management
- Support for both face and body animations
- Progress tracking and error handling
- Configurable through environment variables

## Prerequisites

- Unreal Engine 5.1 or later
- Python 3.7+
- FTrack account (optional)
- MetaHuman Plugin installed in your Unreal project

## Installation

### 1. Install in Unreal Project

1. Navigate to your Unreal Project's Python folder:
   ```bash
   cd <YourProject>/Content/Python/
   ```

2. Clone this repository:
   ```bash
   git clone <repository-url>
   ```

### 2. Configure Environment

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` with your settings

### 3. Install Dependencies

```bash
pip install -e .[dev]
```

## Usage

### Python Console

1. Open Unreal Engine
2. Window → Developer Tools → Python Console
3. Run:
   ```python
   import mha_batch_importer
   mha_batch_importer.run()
   ```

### Editor Utility Widget

1. Create Editor Utility Widget
2. Add button
3. Add to clicked event:
   ```python
   import mha_batch_importer
   mha_batch_importer.run()
   ```

## Configuration

### FTrack Setup

1. Required Custom Attributes:
   - actor_names (Text)
   - mhid_path (Text)
   - skeletal_mesh_path (Text)

2. Environment Variables:
   - FTRACK_SERVER
   - FTRACK_API_KEY
   - FTRACK_API_USER
   - FTRACK_PROJECT_ID

### Local Setup

Configure in `config/settings.py`:
- Character mappings
- Asset paths
- Import settings

## Development

### Setup

```bash
# Install dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Code Style

```bash
# Run style checks
flake8 .
black .
isort .
```

### Testing

```bash
pytest
```

## Troubleshooting

### Common Issues

1. Module Not Found
   - Check Python path in Project Settings
   - Verify Content/Python installation
   - Check Python environment

2. FTrack Connection
   - Verify credentials
   - Check network connection
   - Confirm API permissions

3. Import Failures
   - Verify file paths
   - Check MetaHuman Plugin status
   - Review Unreal Engine logs

## Support

Report issues through the repository issue tracker.

## License

See LICENSE file for details