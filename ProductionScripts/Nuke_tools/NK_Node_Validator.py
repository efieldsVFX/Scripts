import nuke
import hashlib
import json
import logging
import yaml
import time
import os
from pathlib import Path
from contextlib import contextmanager
from typing import List, Dict, Optional, Generator
from datetime import datetime

# After imports, before constants
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers if you want to log to both console and file
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Constants
CONFIG_PATH = Path(__file__).parent / "config" / "validator_config.yaml"
BACKUP_DIR = Path(__file__).parent / "backups"
DEFAULT_CONFIG = {
    "filtered_node_types": ["BackdropNode", "NoOp", "Dot"],
    "backup_enabled": True,
    "max_backups": 5,
    "progress_update_frequency": 10,  # Update every 10 nodes
}

class ValidationConfig:
    """Manages configuration settings"""
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r') as f:
                    return yaml.safe_load(f)
            return DEFAULT_CONFIG
        except Exception as e:
            logger.warning(f"Failed to load config, using defaults: {e}")
            return DEFAULT_CONFIG
            
    @property
    def filtered_types(self) -> List[str]:
        return self.config.get('filtered_node_types', DEFAULT_CONFIG['filtered_node_types'])

class BackupManager:
    """Handles script backups and restoration"""
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self) -> Path:
        """Creates a backup of current script"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"backup_{timestamp}.nk"
        
        try:
            nuke.scriptSave(str(backup_path))
            self._cleanup_old_backups()
            logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
            
    def _cleanup_old_backups(self):
        """Maintains only recent backups"""
        backups = sorted(self.backup_dir.glob("backup_*.nk"))
        max_backups = config.config.get('max_backups', DEFAULT_CONFIG['max_backups'])
        
        for old_backup in backups[:-max_backups]:
            old_backup.unlink()

class ProgressTracker:
    """Tracks and displays operation progress"""
    def __init__(self, total: int, task_name: str):
        self.total = total
        self.current = 0
        self.task_name = task_name
        self.start_time = time.time()
        self.panel = nuke.ProgressTask(task_name)
        
    def update(self, increment: int = 1) -> bool:
        """Updates progress and returns False if cancelled"""
        self.current += increment
        percentage = int((self.current / self.total) * 100)
        
        if self.panel.isCancelled():
            logger.info("Operation cancelled by user")
            return False
            
        self.panel.setProgress(percentage)
        return True
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        logger.info(f"{self.task_name} completed in {duration:.2f}s")
        del self.panel

class BatchProcessor:
    """Handles batch processing of large node graphs"""
    def __init__(self, batch_size: int = 50):
        self.batch_size = batch_size
        
    def process_in_batches(self, nodes: List[nuke.Node]) -> Generator[List[nuke.Node], None, None]:
        """Process nodes in batches to prevent UI freezing"""
        current_batch = []
        for node in nodes:
            current_batch.append(node)
            if len(current_batch) >= self.batch_size:
                yield current_batch
                current_batch = []
        if current_batch:
            yield current_batch

class NodeValidator:
    """Main validation logic with enhanced features"""
    def __init__(self):
        self.config = ValidationConfig()
        self.backup_mgr = BackupManager()
        self.batch_processor = BatchProcessor()
        
    def validate_nodes(self) -> Dict[str, List[str]]:
        """Main validation method with batch processing"""
        try:
            if self.config.config['backup_enabled']:
                self.backup_mgr.create_backup()
            
            original_nodes = nuke.allNodes(recurseGroups=True)
            if not original_nodes:
                raise ValueError("No nodes found in scene")
                
            results = {
                'problematic_nodes': [],
                'validation_errors': [],
                'performance_metrics': [],
                'processed_count': 0
            }
            
            with ProgressTracker(len(original_nodes), "Validating Nodes") as progress:
                for batch in self.batch_processor.process_in_batches(original_nodes):
                    if not progress.update(len(batch)):
                        raise InterruptedError("Validation cancelled by user")
                        
                    self._validate_batch(batch, results)
                    results['processed_count'] += len(batch)
                    
                    # Allow UI updates between batches
                    nuke.executeInMainThread(lambda: None)
                        
            return results
        except Exception as e:
            logger.error(f"Node validation failed: {e}")
            raise
            
    def _validate_batch(self, batch: List[nuke.Node], results: Dict[str, List[str]]):
        """Validates a batch of nodes"""
        for node in self._process_nodes(batch):
            try:
                if self._is_problematic(node):
                    results['problematic_nodes'].append(node.name())
            except Exception as e:
                results['validation_errors'].append(f"{node.name()}: {str(e)}")

    def show_results(self, results: Dict[str, List[str]]):
        """Enhanced results display using Nuke's native panel system"""
        panel = nuke.Panel('Validation Results')
        
        # Summary section
        panel.addSingleLineText('Total Processed:', str(results['processed_count']))
        panel.addSingleLineText('Issues Found:', str(len(results['problematic_nodes'])))
        
        # Problematic nodes section
        if results['problematic_nodes']:
            panel.addMultilineTextInput('Problematic Nodes:', 
                                      '\n'.join(results['problematic_nodes']))
        
        # Errors section
        if results['validation_errors']:
            panel.addMultilineTextInput('Validation Errors:', 
                                      '\n'.join(results['validation_errors']))
            
        # Performance metrics
        if results['performance_metrics']:
            panel.addMultilineTextInput('Performance Metrics:', 
                                      '\n'.join(results['performance_metrics']))
        
        # Add action buttons
        panel.addButton('Export Report')
        panel.addButton('Close')
        
        result = panel.show()
        
        # Handle export if requested
        if result == 0:  # Export button clicked
            self._export_results(results)
            
    def _export_results(self, results: Dict[str, List[str]]):
        """Exports validation results to a file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = Path(nuke.script_directory()) / f"validation_report_{timestamp}.txt"
            
            with open(export_path, 'w') as f:
                f.write("Node Validation Report\n")
                f.write("=" * 20 + "\n\n")
                
                f.write(f"Total Nodes Processed: {results['processed_count']}\n")
                f.write(f"Issues Found: {len(results['problematic_nodes'])}\n\n")
                
                if results['problematic_nodes']:
                    f.write("Problematic Nodes:\n")
                    f.write("\n".join(f"- {node}" for node in results['problematic_nodes']))
                    f.write("\n\n")
                    
                if results['validation_errors']:
                    f.write("Validation Errors:\n")
                    f.write("\n".join(f"- {error}" for error in results['validation_errors']))
                    
            nuke.message(f"Report exported to:\n{export_path}")
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            nuke.message("Failed to export results")

    def _process_nodes(self, nodes: List[nuke.Node]) -> Generator[nuke.Node, None, None]:
        """Processes nodes with batching support"""
        for node in nodes:
            if node.Class() not in self.config.filtered_types:
                yield node
                
    def _is_problematic(self, node: nuke.Node) -> bool:
        """Enhanced node validation logic"""
        try:
            # Check for disconnected input connections
            for i in range(node.maxInputs()):
                if node.input(i) is None and not node.Class() in ['Read', 'Constant', 'ColorWheel']:
                    logger.warning(f"{node.name()}: Input {i} is disconnected")
                    return True

            # Check for disabled but connected nodes
            if node.knob('disable') and node.knob('disable').value() and (node.inputs() or node.dependent()):
                logger.warning(f"{node.name()}: Node is disabled but connected in active chain")
                return True

            # Check for missing file paths in Read/Write nodes
            if node.Class() in ['Read', 'Write']:
                file_knob = node.knob('file')
                if not file_knob or not file_knob.value():
                    logger.warning(f"{node.name()}: Missing file path")
                    return True
                if node.Class() == 'Read' and not os.path.exists(file_knob.evaluate()):
                    logger.warning(f"{node.name()}: File path does not exist: {file_knob.evaluate()}")
                    return True

            # Check for expression errors
            for knob in node.allKnobs():
                if knob.hasExpression():
                    try:
                        knob.evaluate()
                    except Exception:
                        logger.warning(f"{node.name()}: Expression error in knob {knob.name()}")
                        return True

            # Check for performance-impacting settings
            if node.Class() == 'Blur' and node.knob('size').value() > 100:
                logger.warning(f"{node.name()}: Large blur size may impact performance")
                return True

            # Check for colorspace mismatches
            if node.Class() in ['Read', 'Write'] and node.knob('colorspace'):
                if node.knob('colorspace').value() == 'default':
                    logger.warning(f"{node.name()}: Using default colorspace")
                    return True

            # Check for merged nodes without masks
            if node.Class() == 'Merge2' and node.knob('operation').value() != 'copy':
                if not node.input(2):  # mask input
                    logger.warning(f"{node.name()}: Merge operation without mask")
                    return True

            return False

        except Exception as e:
            logger.error(f"Validation failed for node {node.name()}: {e}")
            return True
            
def run_validation():
    """Entry point with error handling"""
    try:
        validator = NodeValidator()
        results = validator.validate_nodes()
        validator.show_results(results)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        nuke.message(f"Validation failed: {str(e)}")

if __name__ == "__main__":
    run_validation()
