# Unreal Engine Metahuman Tools

Advanced Metahuman batch import and management tools for Unreal Engine. Last Updated: December 19, 2024

## 🎭 Components

### Batch Importer (`MHA_Batch_Importer/`)
- **Batch Processing**
  - Multiple metahuman import
  - Asset validation
  - Progress tracking
  - Error handling

- **Pipeline Integration**
  - Project structure management
  - Asset organization
  - Version control
  - Logging system

## 🔧 Features

### Asset Management
- Batch metahuman importing
- Asset organization
- Version tracking
- Progress monitoring

### Pipeline Integration
- Project structure setup
- Asset validation
- Error handling
- Logging system

### User Interface
- Modern Qt interface
- Progress visualization
- Error notifications
- Status updates

## 📸 Visual Guide

### Batch Import Workflow
1. **Select Import Type**  
   Choose between face or body animation import modes:
   ![Import Type Selection](MHA_Batch_Importer/docs/images/0_Choice.png)

2. **Input Selection**  
   Either select folders for bulk import:
   ![Folder Selection](MHA_Batch_Importer/docs/images/1_Folders.png)

   Or choose specific capture data assets:
   ![Asset Selection](MHA_Batch_Importer/docs/images/2_CaptureDataAssets.png)

3. **Asset Search**  
   Use the search functionality to filter assets:
   ![Search Function](MHA_Batch_Importer/docs/images/3_Search.png)

4. **Processing**  
   Monitor real-time import progress:
   ![Progress Dialog](MHA_Batch_Importer/docs/images/4_Progress.png)

5. **Completion**  
   Review completed imports:
   ![Completion Status](MHA_Batch_Importer/docs/images/5_Complete.png)

6. **Results in Unreal Engine**  
   Processed performance in the engine:
   ![Processed Performance](MHA_Batch_Importer/docs/images/6_ProcessedPerformance.png)

   Generated animation sequence:
   ![Exported Animation](MHA_Batch_Importer/docs/images/7_ExportedAnim.png)

## 💻 Requirements
- Unreal Engine 5.4+
- Python 3.7+
- Qt/PySide2
- Network access for asset management

## 🚀 Usage

```python
from Metahuman_tools import batch_importer
batch_importer.run_batch_import()
```

## 📝 License
Internal use only - All rights reserved.

## Author
**Eric Fields** - Pipeline Technical Director  
Contact: [efieldsvfx@gmail.com](mailto:efieldsvfx@gmail.com)
