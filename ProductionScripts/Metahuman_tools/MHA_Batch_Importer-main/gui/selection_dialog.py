"""Dialog for selecting folders or assets to process."""

from PySide6 import QtWidgets, QtCore, QtGui
from ..utils.logging_config import logger

class UnifiedSelectionDialog(QtWidgets.QDialog):
    def __init__(self, available_folders, capture_data_assets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Items for Processing")
        self.setGeometry(300, 300, 800, 600)
        self.available_folders = available_folders
        self.capture_data_assets = capture_data_assets
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI elements."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Info label at top
        info_label = QtWidgets.QLabel(
            "Select folders and/or assets to process. Use checkboxes to make selections."
        )
        info_label.setStyleSheet("color: white; padding: 5px;")
        layout.addWidget(info_label)

        # Search bar
        search_layout = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("Search:")
        search_label.setStyleSheet("color: white;")
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                padding: 4px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_tree)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Tree widget
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabel("Available Items")
        layout.addWidget(self.tree)

        # Selection info label
        self.selection_info = QtWidgets.QLabel("No items selected")
        self.selection_info.setStyleSheet("color: white; padding: 5px;")
        layout.addWidget(self.selection_info)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        # Create utility buttons (smaller size)
        self.select_all_button = QtWidgets.QPushButton("Select All")
        self.select_none_button = QtWidgets.QPushButton("Reset")
        
        # Make utility buttons smaller
        utility_button_size = """
            min-width: 70px;
            max-width: 70px;
            padding: 3px 10px;
        """
        
        # Style Select All button
        self.select_all_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #2a5699;
                color: white;
                border: none;
                border-radius: 3px;
                {utility_button_size}
            }}
            QPushButton:hover {{
                background-color: #3267b5;
            }}
            QPushButton:pressed {{
                background-color: #1f4277;
            }}
        """)
        
        # Style Reset button
        self.select_none_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 3px;
                {utility_button_size}
            }}
            QPushButton:hover {{
                background-color: #777777;
            }}
            QPushButton:pressed {{
                background-color: #555555;
            }}
        """)
        
        # Add utility buttons to layout
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.select_none_button)
        button_layout.addStretch()
        
        # Create and style OK/Cancel buttons (larger size)
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        
        main_button_size = """
            min-width: 90px;
            max-width: 90px;
            padding: 5px 15px;
        """
        
        # Style OK button
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #2d8659;
                color: white;
                border: none;
                border-radius: 3px;
                {main_button_size}
            }}
            QPushButton:hover {{
                background-color: #35a06a;
            }}
            QPushButton:pressed {{
                background-color: #246c47;
            }}
            QPushButton:disabled {{
                background-color: #666666;
                color: #888888;
            }}
        """)
        
        # Style Cancel button
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #994444;
                color: white;
                border: none;
                border-radius: 3px;
                {main_button_size}
            }}
            QPushButton:hover {{
                background-color: #b25050;
            }}
            QPushButton:pressed {{
                background-color: #803939;
            }}
        """)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.tree.itemChanged.connect(self.update_selection_info)
        self.select_all_button.clicked.connect(self.select_all_items)
        self.select_none_button.clicked.connect(self.select_no_items)

        # Populate tree
        self.populate_tree()

    def populate_tree(self):
        """Populate the tree with folders and assets."""
        self.tree.clear()
        tree_dict = {}

        # Add folders to the tree
        for folder in self.available_folders:
            parts = folder.split('/')
            current_dict = tree_dict
            for part in parts:
                if part not in current_dict:
                    current_dict[part] = {
                        'name': part,
                        'children': {}
                    }
                current_dict = current_dict[part]['children']

        # Add assets to the tree
        for asset in self.capture_data_assets:
            asset_name = asset.get_name()
            asset_path = asset.package_path
            parts = asset_path.split('/')
            current_dict = tree_dict
            parent_dict = None
            for i, part in enumerate(parts[:-1]):  # Exclude the asset name
                if part not in current_dict:
                    current_path = '/'.join(parts[:i+1])
                    current_dict[part] = {
                        'name': part,
                        'full_path': f"/Game/{current_path}",
                        'children': {},
                        'assets': []
                    }
                parent_dict = current_dict[part]  # Keep reference to the parent folder dict
                current_dict = current_dict[part]['children']

            # Now parent_dict is the folder dict; add asset here
            if parent_dict:
                parent_dict['assets'].append(asset)
            else:
                logger.warning(f"Parent folder not found for asset: {asset}")

        # Create tree items from the unified dictionary structure
        self._create_tree_items(tree_dict, self.tree)
        self.tree.collapseAll()

    def _create_tree_items(self, data, parent=None):
        """Recursively create tree items from the dictionary structure."""
        if parent is None:
            parent = self.tree

        for key, value in data.items():
            # Create folder item
            folder_item = QtWidgets.QTreeWidgetItem([key])
            folder_item.setFlags(folder_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            folder_item.setCheckState(0, QtCore.Qt.Unchecked)
            
            # Store the full path in the item's data
            folder_item.setData(0, QtCore.Qt.UserRole, value.get('full_path', ''))
            parent.addTopLevelItem(folder_item) if isinstance(parent, QtWidgets.QTreeWidget) else parent.addChild(folder_item)

            # Add assets under this folder
            if value.get('assets'):
                for asset in value['assets']:
                    asset_item = QtWidgets.QTreeWidgetItem([asset.get_name()])
                    asset_item.setFlags(asset_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    asset_item.setCheckState(0, QtCore.Qt.Unchecked)
                    asset_item.setData(0, QtCore.Qt.UserRole, asset)
                    folder_item.addChild(asset_item)

            # Recursively process children folders
            if value['children']:
                self._create_tree_items(value['children'], folder_item)

    def filter_tree(self, filter_text):
        """Filter the tree based on search text."""
        def filter_item(item, text):
            if text.lower() in item.text(0).lower():
                item.setHidden(False)
                parent = item.parent()
                while parent:
                    parent.setHidden(False)
                    parent = parent.parent()
                return True
            
            child_match = False
            for i in range(item.childCount()):
                if filter_item(item.child(i), text):
                    child_match = True
            
            item.setHidden(not child_match)
            return child_match

        for i in range(self.tree.topLevelItemCount()):
            filter_item(self.tree.topLevelItem(i), filter_text)

    def update_selection_info(self, item=None):
        """Update the selection information label based on checked items."""
        selected = self.get_selected_items()
        
        info_parts = []
        if selected['folders']:
            info_parts.append(f"Folders: {len(selected['folders'])}")
        if selected['assets']:
            info_parts.append(f"Assets: {len(selected['assets'])}")
            
        if info_parts:
            self.selection_info.setText("Selected: " + " | ".join(info_parts))
            self.ok_button.setEnabled(True)
        else:
            self.selection_info.setText("No items selected")
            self.ok_button.setEnabled(False)

    def get_selected_items(self):
        """Return checked folders and assets."""
        selected_data = {'folders': [], 'assets': []}

        def process_item(item):
            if item.checkState(0) == QtCore.Qt.Checked:
                item_data = item.data(0, QtCore.Qt.UserRole)
                if isinstance(item_data, str):
                    # This is a folder
                    selected_data['folders'].append(item_data)
                else:
                    # This is an asset
                    selected_data['assets'].append(item_data)
            
            # Process children
            for i in range(item.childCount()):
                process_item(item.child(i))

        # Process all top-level items
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            process_item(root.child(i))

        return selected_data

    def update_view(self):
        """Update the view based on selected radio button"""
        if hasattr(self, 'folder_list'):
            self.folder_list.setVisible(self.folder_radio.isChecked())
        if hasattr(self, 'asset_list'):
            self.asset_list.setVisible(self.asset_radio.isChecked())

    def get_selections(self):
        """Get selected folders and assets."""
        selections = {
            'folders': [],
            'assets': []
        }
        
        def process_item(item):
            if item.checkState(0) == QtCore.Qt.Checked:
                data = item.data(0, QtCore.Qt.UserRole)
                if isinstance(data, str):  # It's a folder path
                    selections['folders'].append(data)
                else:  # It's an asset
                    selections['assets'].append(data)
            
            # Process child items
            for i in range(item.childCount()):
                process_item(item.child(i))
        
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            process_item(root.child(i))
        
        return selections

    def select_all_items(self):
        """Select all items in the tree."""
        self._set_check_state_recursive(self.tree.invisibleRootItem(), QtCore.Qt.Checked)
        self.update_selection_info()

    def select_no_items(self):
        """Deselect all items in the tree."""
        self._set_check_state_recursive(self.tree.invisibleRootItem(), QtCore.Qt.Unchecked)
        self.update_selection_info()

    def _set_check_state_recursive(self, item, state):
        """Recursively set the check state of an item and all its children."""
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self._set_check_state_recursive(child, state)