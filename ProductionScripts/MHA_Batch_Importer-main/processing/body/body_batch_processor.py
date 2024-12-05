"""Handles batch processing of animation files."""

import unreal
from PySide6 import QtCore
from .body_processor import BodyProcessor
from ...utils.logging_config import logger


class BodyBatchProcessor(QtCore.QObject):
    """Manages batch processing of animation files."""

    progress_updated = QtCore.Signal(int, str, str, str)
    processing_finished = QtCore.Signal()
    error_occurred = QtCore.Signal(str)

    def __init__(self):
        """Initialize the batch processor."""
        super().__init__()
        self.processor = BodyProcessor()
        self.animation_files = []
        self.current_index = 0

    def run_batch_process(self, file_paths: list, character_name: str) -> None:
        """
        Start batch processing of animation files.

        Args:
            file_paths: List of animation file paths to process
            character_name: Target character name
        """
        try:
            self.animation_files = file_paths
            self.current_index = 0

            if not self.animation_files:
                logger.error("No animation files provided for processing")
                return

            logger.info(f"Beginning batch process for {len(self.animation_files)} files")
            QtCore.QTimer.singleShot(0, lambda: self._process_next_file(character_name))

        except Exception as e:
            logger.error(f"Batch process initialization failed: {str(e)}")
            self.error_occurred.emit(str(e))

    def _process_next_file(self, character_name: str) -> None:
        """Process the next animation file in the queue."""
        try:
            if self.current_index >= len(self.animation_files):
                self.processing_finished.emit()
                return

            current_file = self.animation_files[self.current_index]
            self._update_progress("Processing", current_file)

            sequence = self.processor.process_asset(current_file, character_name)
            self._handle_processing_result(sequence, current_file)

            self.current_index += 1
            QtCore.QTimer.singleShot(0, lambda: self._process_next_file(character_name))

        except Exception as e:
            logger.error(f"File processing error: {str(e)}")
            self._update_progress("Failed", str(e))
            self.current_index += 1
            QtCore.QTimer.singleShot(0, lambda: self._process_next_file(character_name))

    def _update_progress(self, status: str, message: str) -> None:
        """Update processing progress."""
        self.progress_updated.emit(
            self.current_index,
            f"{status} {self.current_index + 1}/{len(self.animation_files)}",
            message,
            'processing'
        )

    def _handle_processing_result(self, sequence, file_path: str) -> None:
        """Handle the result of processing an animation file."""
        if sequence:
            self._update_progress("Complete", f"Processed: {sequence.get_name()}")
        else:
            self._update_progress("Failed", f"Failed to process: {file_path}") 