"""Verification script for batch_metahuman_importer package."""

import os
import sys
import importlib
from pathlib import Path

def verify_imports():
    """Verify all required imports."""
    required_imports = [
        'batch_metahuman_importer.run',
        'batch_metahuman_importer.processing.body.body_processor',
        'batch_metahuman_importer.processing.face.face_processor',
        'batch_metahuman_importer.gui.main_ui'
    ]
    
    for module in required_imports:
        try:
            importlib.import_module(module)
            print(f"✓ Successfully imported {module}")
        except ImportError as e:
            print(f"✗ Failed to import {module}: {str(e)}")
            return False
    return True

def verify_file_structure():
    """Verify all required files exist."""
    base_path = Path(__file__).parent.parent
    
    required_files = [
        '__init__.py',
        'run.py',
        'processing/__init__.py',
        'processing/base/__init__.py',
        'processing/base/base_processor.py',
        'processing/base/base_helper.py',
        'processing/body/__init__.py',
        'processing/body/body_processor.py',
        'processing/body/body_helper.py',
        'processing/body/body_batch_processor.py',
        'processing/face/__init__.py',
        'processing/face/face_processor.py',
        'gui/__init__.py',
        'gui/main_ui.py',
        'gui/progress_dialog.py',
        'utils/__init__.py',
        'utils/constants.py',
        'utils/logging_config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not (base_path / file).exists():
            missing_files.append(file)
            
    if missing_files:
        print("\nMissing files:")
        for file in missing_files:
            print(f"✗ {file}")
        return False
        
    print("\nAll required files present")
    return True

def verify_class_structure():
    """Verify class inheritance and methods."""
    try:
        from batch_metahuman_importer.processing.body.body_processor import BodyProcessor
        from batch_metahuman_importer.processing.base.base_processor import BaseProcessor
        
        # Verify inheritance
        if not issubclass(BodyProcessor, BaseProcessor):
            print("✗ BodyProcessor does not inherit from BaseProcessor")
            return False
            
        # Verify required methods
        required_methods = ['process_asset', 'get_target_skeletal_mesh']
        for method in required_methods:
            if not hasattr(BodyProcessor, method):
                print(f"✗ BodyProcessor missing required method: {method}")
                return False
                
        print("\nClass structure verified")
        return True
        
    except Exception as e:
        print(f"✗ Class structure verification failed: {str(e)}")
        return False

def run_verification():
    """Run all verification checks."""
    print("Starting package verification...\n")
    
    imports_ok = verify_imports()
    files_ok = verify_file_structure()
    classes_ok = verify_class_structure()
    
    if all([imports_ok, files_ok, classes_ok]):
        print("\n✓ All verification checks passed")
        return True
    else:
        print("\n✗ Some verification checks failed")
        return False

if __name__ == "__main__":
    sys.exit(0 if run_verification() else 1) 