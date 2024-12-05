"""
Task Mover - A tool for moving tasks between projects in a project management system.
Handles task hierarchies, dates, and relationships while maintaining data integrity.
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any
import ftrack_api
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QSplitter,
    QProgressBar,
    QLabel
)
from PyQt5.QtCore import Qt


class TaskMoverException(Exception):
    """Custom exception for TaskMover-specific errors."""
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)


class TaskMover(QMainWindow):
    """Main window for the Task Mover application."""

    def __init__(
        self,
        source_structure: List[Dict[str, Any]],
        target_structure: List[Dict[str, Any]],
        session: ftrack_api.Session
    ) -> None:
        """Initialize the TaskMover window.

        Args:
            source_structure: List of dictionaries containing source project structure
            target_structure: List of dictionaries containing target project structure
            session: Active ftrack session for database operations
        """
        super().__init__()
        self.source_structure = source_structure
        self.target_structure = target_structure
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface components."""
        self.setWindowTitle('Project Task Manager')
        self.setGeometry(100, 100, 1200, 600)

        # Create tree widgets
        self.source_tree = self._create_tree_widget("Source Project")
        self.target_tree = self._create_tree_widget("Target Project")

        # Set up progress tracking
        self.progress_label = QLabel('Progress:', self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # Create layout
        self._setup_layout()

    def _create_tree_widget(self, label: str) -> QTreeWidget:
        """Create and configure a tree widget.
        
        Args:
            label: Header label for the tree widget
            
        Returns:
            Configured QTreeWidget instance
        """
        tree = QTreeWidget(self)
        tree.setColumnCount(1)
        tree.setHeaderLabels([label])
        return tree

    def _setup_layout(self) -> None:
        """Set up the main window layout."""
        # Create splitter for tree views
        splitter = QSplitter()
        splitter.addWidget(self.source_tree)
        splitter.addWidget(self.target_tree)

        # Create move button
        move_button = QPushButton('Move Selected Tasks', self)
        move_button.clicked.connect(self.move_tasks)

        # Set up main layout
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(move_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def move_tasks(self) -> None:
        """Handle the task movement operation with proper error handling."""
        selected_items = self.source_tree.selectedItems()
        target_item = self.target_tree.currentItem()
        
        try:
            self._validate_selection(selected_items, target_item)
            self._process_task_movement(selected_items, target_item)
        except TaskMoverException as e:
            self.logger.error(f"Task movement failed: {str(e)}")
        except Exception as e:
            self.logger.exception("Unexpected error during task movement")
            
    def _validate_selection(
        self,
        selected_items: List[QTreeWidgetItem],
        target_item: Optional[QTreeWidgetItem]
    ) -> None:
        """Validate the selected items before processing.
        
        Args:
            selected_items: List of selected items from source tree
            target_item: Selected target location
            
        Raises:
            TaskMoverException: If validation fails
        """
        if not selected_items:
            raise TaskMoverException("No source items selected")
        if not target_item:
            raise TaskMoverException("No target location selected")

    def _process_task_movement(
        self,
        selected_items: List[QTreeWidgetItem],
        target_item: QTreeWidgetItem
    ) -> None:
        """Process the movement of selected tasks.
        
        Args:
            selected_items: List of items to move
            target_item: Destination for items
        """
        target_entity = target_item.data(0, 1)
        total_items = len(selected_items)
        self.progress_bar.setMaximum(total_items)
        
        failed_items = []
        for idx, item in enumerate(selected_items):
            try:
                entity = item.data(0, 1)
                self._copy_entity(entity, target_entity)
                self.logger.info(f"Successfully copied {entity['name']}")
            except Exception as e:
                failed_items.append((entity['name'], str(e)))
                self.logger.error(f"Failed to copy {entity['name']}: {str(e)}")
            finally:
                self.progress_bar.setValue(idx + 1)
                QApplication.processEvents()

        self._handle_operation_results(failed_items)

    def _handle_operation_results(self, failed_items: List[tuple]) -> None:
        """Handle the results of the task movement operation.
        
        Args:
            failed_items: List of tuples containing (item_name, error_message)
        """
        if failed_items:
            self.logger.error(f"Failed to copy {len(failed_items)} items: {failed_items}")
        else:
            self.logger.info("Task movement completed successfully")
            self.session.commit()

    def _copy_entity(
        self,
        entity: Dict[str, Any],
        target_parent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Copy an entity and its children to a new location.
        
        Args:
            entity: Source entity to copy
            target_parent: Target parent entity
            
        Returns:
            Dict containing the newly created entity
            
        Raises:
            TaskMoverException: If entity copying fails
        """
        try:
            entity_type = entity.entity_type
            entity_data = self._prepare_entity_data(entity, target_parent)

            if entity_type == 'Task':
                self._adjust_task_dates(entity_data, entity, target_parent)

            self.logger.debug(
                f"Creating new {entity_type} with data: {entity_data}"
            )
            new_entity = self.session.create(entity_type, entity_data)

            # Process any child entities
            for child in entity.get('children', []):
                self._copy_entity(child, new_entity)

            return new_entity

        except Exception as e:
            error_msg = f"Failed to copy entity {entity.get('name', 'unknown')}"
            self.logger.exception(error_msg)
            raise TaskMoverException(f"{error_msg}: {str(e)}")

    def _prepare_entity_data(
        self,
        entity: Dict[str, Any],
        target_parent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare entity data for copying.
        
        Args:
            entity: Source entity
            target_parent: Target parent entity
            
        Returns:
            Dict containing prepared entity data
        """
        return {
            'name': entity.get('name'),
            'parent_id': target_parent.get('id'),
            'type_id': entity.get('type_id'),
            'status_id': entity.get('status_id'),
            'bid': entity.get('bid', 0.0),
            'time_logged': entity.get('time_logged', 0.0),
            'description': entity.get('description', ''),
            'priority_id': entity.get('priority_id'),
            'object_type_id': entity.get('object_type_id')
        }

    def _adjust_task_dates(
        self,
        entity_data: Dict[str, Any],
        source_entity: Dict[str, Any],
        target_parent: Dict[str, Any]
    ) -> None:
        """Adjust task dates to fit within project timeline.
        
        Args:
            entity_data: Entity data to be updated
            source_entity: Source entity containing original dates
            target_parent: Target parent entity for date constraints
            
        Raises:
            TaskMoverException: If date adjustment fails
        """
        try:
            project = self._get_project_from_entity(target_parent)
            project_start = project.get('start_date')
            project_end = project.get('end_date')

            if not all([project_start, project_end]):
                self.logger.warning("Project dates not set, skipping date adjustment")
                return

            start_date = self._validate_and_adjust_date(
                source_entity.get('start_date'),
                project_start,
                project_end,
                'start'
            )
            if start_date:
                entity_data['start_date'] = start_date

            end_date = self._validate_and_adjust_date(
                source_entity.get('end_date'),
                project_start,
                project_end,
                'end'
            )
            if end_date:
                entity_data['end_date'] = end_date

        except Exception as e:
            error_msg = "Failed to adjust task dates"
            self.logger.exception(error_msg)
            raise TaskMoverException(f"{error_msg}: {str(e)}")

    def _get_project_from_entity(
        self,
        entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get the project entity from any child entity.
        
        Args:
            entity: Entity to find project for
            
        Returns:
            Project entity
            
        Raises:
            TaskMoverException: If project cannot be found
        """
        try:
            current = entity
            while current.get('parent'):
                if current.entity_type == 'Project':
                    return current
                current = current['parent']

            if current.entity_type == 'Project':
                return current

            raise TaskMoverException("Could not find parent project")

        except Exception as e:
            error_msg = "Failed to retrieve parent project"
            self.logger.exception(error_msg)
            raise TaskMoverException(f"{error_msg}: {str(e)}")

    def _validate_and_adjust_date(
        self,
        date: Optional[str],
        project_start: str,
        project_end: str,
        date_type: str
    ) -> Optional[str]:
        """Validate and adjust a date to fit within project timeline.
        
        Args:
            date: Date to validate
            project_start: Project start date
            project_end: Project end date
            date_type: Type of date ('start' or 'end')
            
        Returns:
            Adjusted date or None if date is invalid
        """
        if not date:
            return None

        try:
            if date < project_start:
                self.logger.warning(
                    f"Task {date_type} date {date} before project start, "
                    f"adjusting to {project_start}"
                )
                return project_start

            if date > project_end:
                self.logger.warning(
                    f"Task {date_type} date {date} after project end, "
                    f"adjusting to {project_end}"
                )
                return project_end

            return date

        except Exception as e:
            self.logger.warning(
                f"Failed to validate {date_type} date: {str(e)}, using None"
            )
            return None

    def _load_project_structure(self) -> None:
        """Load project structure into tree widgets."""
        try:
            self._populate_tree(
                self.source_tree,
                self.source_structure
            )
            self._populate_tree(
                self.target_tree,
                self.target_structure
            )
        except Exception as e:
            error_msg = "Failed to load project structure"
            self.logger.exception(error_msg)
            raise TaskMoverException(f"{error_msg}: {str(e)}")

    def _populate_tree(
        self,
        tree: QTreeWidget,
        structure: List[Dict[str, Any]]
    ) -> None:
        """Populate a tree widget with project structure.
        
        Args:
            tree: Tree widget to populate
            structure: Project structure data
        """
        tree.clear()
        for item in structure:
            tree_item = self._create_tree_item(item)
            tree.addTopLevelItem(tree_item)

    def _create_tree_item(
        self,
        item_data: Dict[str, Any]
    ) -> QTreeWidgetItem:
        """Create a tree widget item from entity data.
        
        Args:
            item_data: Dictionary containing entity data
            
        Returns:
            Configured QTreeWidgetItem
            
        Raises:
            TaskMoverException: If item creation fails
        """
        try:
            tree_item = QTreeWidgetItem([item_data.get('name', '')])
            tree_item.setData(0, Qt.UserRole, item_data)
            
            # Recursively add child items
            if 'children' in item_data:
                for child in item_data['children']:
                    child_item = self._create_tree_item(child)
                    tree_item.addChild(child_item)
            
            return tree_item
            
        except Exception as e:
            error_msg = f"Failed to create tree item for {item_data.get('name', 'unknown')}"
            self.logger.exception(error_msg)
            raise TaskMoverException(f"{error_msg}: {str(e)}")

    def _update_progress(
        self,
        current: int,
        total: int,
        message: str = ''
    ) -> None:
        """Update the progress bar and message.
        
        Args:
            current: Current progress value
            total: Total number of items
            message: Optional status message
        """
        try:
            percentage = (current / total) * 100
            self.progress_bar.setValue(int(percentage))
            
            if message:
                self.progress_label.setText(message)
                
            # Ensure UI updates are processed
            QApplication.processEvents()
            
        except Exception as e:
            self.logger.warning(f"Failed to update progress: {str(e)}")

    def _cleanup_session(self) -> None:
        """Clean up the session and handle any pending changes."""
        try:
            if self.session.has_pending_changes():
                self.logger.info("Committing pending changes")
                self.session.commit()
                
        except Exception as e:
            error_msg = "Failed to cleanup session"
            self.logger.exception(error_msg)
            raise TaskMoverException(f"{error_msg}: {str(e)}")

    def closeEvent(self, event: Any) -> None:
        """Handle application closure.
        
        Args:
            event: Close event from Qt
        """
        try:
            self._cleanup_session()
            self.logger.info("Application closed successfully")
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Error during application closure: {str(e)}")
            event.accept()  # Accept anyway to allow closure


def setup_logging() -> None:
    """Configure logging for the application."""
    try:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('task_mover.log'),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        print(f"Failed to setup logging: {str(e)}")
        sys.exit(1)


def initialize_session() -> ftrack_api.Session:
    """Initialize and return an ftrack session.
    
    Returns:
        Configured ftrack session
        
    Raises:
        TaskMoverException: If session initialization fails
    """
    try:
        server_url = os.getenv('FTRACK_SERVER_URL')
        api_key = os.getenv('FTRACK_API_KEY')
        api_user = os.getenv('FTRACK_API_USER')

        if not all([server_url, api_key, api_user]):
            raise TaskMoverException("Missing required environment variables")

        return ftrack_api.Session(
            server_url=server_url,
            api_key=api_key,
            api_user=api_user
        )
        
    except Exception as e:
        error_msg = "Failed to initialize ftrack session"
        logging.exception(error_msg)
        raise TaskMoverException(f"{error_msg}: {str(e)}")


def get_project_structure(
    session: ftrack_api.Session,
    project_name: str
) -> List[Dict[str, Any]]:
    """Retrieve project structure from ftrack.
    
    Args:
        session: Active ftrack session
        project_name: Name of the project to retrieve
        
    Returns:
        List of dictionaries containing project structure
        
    Raises:
        TaskMoverException: If structure retrieval fails
    """
    try:
        project = session.query(
            f"Project where name is '{project_name}'"
        ).first()
        
        if not project:
            raise TaskMoverException(f"Project '{project_name}' not found")
            
        return _build_structure_tree(project)
        
    except Exception as e:
        error_msg = f"Failed to retrieve project structure for {project_name}"
        logging.exception(error_msg)
        raise TaskMoverException(f"{error_msg}: {str(e)}")


def _build_structure_tree(
    entity: Any,
    depth: int = 0,
    max_depth: int = 10
) -> List[Dict[str, Any]]:
    """Recursively build project structure tree.
    
    Args:
        entity: Current entity to process
        depth: Current depth in tree
        max_depth: Maximum depth to prevent infinite recursion
        
    Returns:
        List of dictionaries containing entity structure
    """
    if depth >= max_depth:
        return []

    try:
        structure = {
            'name': entity.get('name'),
            'id': entity.get('id'),
            'type': entity.entity_type,
            'children': []
        }

        if hasattr(entity, 'children'):
            for child in entity['children']:
                child_structure = _build_structure_tree(
                    child,
                    depth + 1,
                    max_depth
                )
                if child_structure:
                    structure['children'].append(child_structure)

        return structure

    except Exception as e:
        logging.warning(
            f"Failed to build structure for {entity.get('name', 'unknown')}: {str(e)}"
        )
        return {}


def main() -> None:
    """Main application entry point."""
    try:
        # Initialize logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Task Mover application")

        # Initialize session
        session = initialize_session()

        # Get project structures
        source_project = os.getenv('SOURCE_PROJECT', 'Project_A')
        target_project = os.getenv('TARGET_PROJECT', 'Project_B')
        
        source_structure = get_project_structure(session, source_project)
        target_structure = get_project_structure(session, target_project)

        # Initialize Qt application
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = TaskMover(source_structure, target_structure, session)
        window.show()

        # Start event loop
        sys.exit(app.exec_())

    except Exception as e:
        logger.exception("Fatal error in main application")
        sys.exit(1)


if __name__ == '__main__':
    main()
