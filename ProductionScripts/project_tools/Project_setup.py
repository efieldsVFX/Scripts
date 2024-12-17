import sys
import os
import json
import ftrack_api
import logging
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None


def save_config(config_path, config):
    try:
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
    except Exception as e:
        logger.error(f"Error saving config: {e}")


def create_ftrack_project(project_name, project_code, start_date, end_date,
                          server_url, api_key, api_user):
    try:
        session = ftrack_api.Session(
            server_url=server_url,
            api_key=api_key,
            api_user=api_user
        )
        project = session.create('Project', {
            'name': project_name,
            'full_name': project_name,
            'name': project_code,
            'start_date': start_date,
            'end_date': end_date
        })
        session.commit()
        return project, session
    except Exception as e:
        logger.error(f"Error creating Ftrack project: {e}")
        return None, None


def create_ftrack_entities(session, project_id, entities):
    created_entities = {project_id: session.get('Project', project_id)}
    asset_versions = []

    try:
        for entity in entities:
            parent_id = (entity['parent_id'] if entity['parent_id']
                         in created_entities else project_id)
            parent = created_entities[parent_id]

            existing_entity = session.query(
                f"{entity['type']} where name is '{entity['name']}' "
                f"and parent.id is '{parent['id']}'"
            ).first()

            if existing_entity:
                logger.info(
                    f"Entity '{entity['name']}' already exists with ID "
                    f"{existing_entity['id']}. Using existing entity."
                )
                created_entity = existing_entity
            else:
                created_entity = session.create(entity['type'], {
                    'name': entity['name'],
                    'parent': parent
                })
                session.commit()
                logger.info(
                    f"Entity '{entity['name']}' created with ID "
                    f"{created_entity['id']}"
                )

            created_entities[entity['name']] = created_entity

            if entity['type'] == 'Asset':
                asset_type = session.query(
                    'AssetType where name is "Geometry"'
                ).one()
                asset = session.create('Asset', {
                    'name': entity['name'],
                    'type': asset_type,
                    'parent': created_entity
                })
                session.commit()

                default_task = session.query(
                    f'Task where parent.id is "{project_id}"'
                ).first()
                if default_task:
                    asset_version = session.create('AssetVersion', {
                        'asset': asset,
                        'task': default_task
                    })
                    session.commit()
                    asset_versions.append(asset_version)
                else:
                    logger.warning(
                        f"No default task found for project ID {project_id}. "
                        "AssetVersion not created."
                    )

        return created_entities, asset_versions
    except Exception as e:
        logger.error(f"Error creating Ftrack entities: {e}")
        return None, None


def publish_component(session, asset_version, file_path,
                      location_name='ftrack.server'):
    try:
        location = session.query(
            f'Location where name is "{location_name}"'
        ).one()
        component = asset_version.create_component(
            path=file_path,
            data={'name': os.path.basename(file_path)},
            location=location
        )
        session.commit()
        return component
    except Exception as e:
        logger.error(f"Error publishing component: {e}")
        return None


def setup_folder_structure(project_path, structure):
    try:
        for folder in structure:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        logger.info(f"Folder structure created at {project_path}")
    except Exception as e:
        logger.error(f"Error setting up folder structure: {e}")


def create_prism_project(root_path, project_name, project_code, config):
    try:
        project_path = os.path.join(root_path, project_name)
        os.makedirs(project_path, exist_ok=True)
        setup_folder_structure(project_path, config['folder_structure'])
        
        pipeline_json_path = os.path.join(project_path, "00_Pipeline",
                                           "pipeline.json")
        with open(pipeline_json_path, 'w') as json_file:
            pipeline_data = json.dumps(config['pipeline_data'], indent=4).replace(
                '@project_code@', project_code
            )
            json_file.write(pipeline_data)
        
        logger.info(f"pipeline.json created at {pipeline_json_path}")
        return project_path
    except Exception as e:
        logger.error(f"Error creating Prism project: {e}")
        return None


class ProjectSetupApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.config_file_path = 'config.json'
        self.config = load_config(self.config_file_path)
        if not self.config:
            QtWidgets.QMessageBox.critical(self, 'Error',
                                          'Failed to load configuration.')
            sys.exit(1)
        self.init_ui()
        self.session = None
        self.project = None

    def init_ui(self):
        self.setWindowTitle('Project Setup')

        layout = QtWidgets.QVBoxLayout()

        self.project_name_label = QtWidgets.QLabel('Project Name:')
        self.project_name_input = QtWidgets.QLineEdit(self)

        self.project_code_label = QtWidgets.QLabel('Project Code:')
        self.project_code_input = QtWidgets.QLineEdit(self)

        self.start_date_label = QtWidgets.QLabel('Start Date (YYYY-MM-DD):')
        self.start_date_input = QtWidgets.QLineEdit(self)

        self.end_date_label = QtWidgets.QLabel('End Date (YYYY-MM-DD):')
        self.end_date_input = QtWidgets.QLineEdit(self)

        self.thumbnail_label = QtWidgets.QLabel('Project Thumbnail:')
        self.thumbnail_button = QtWidgets.QPushButton('Choose File')
        self.thumbnail_button.clicked.connect(self.choose_thumbnail)
        self.thumbnail_path = ''

        self.create_button = QtWidgets.QPushButton('Create Project', self)
        self.create_button.clicked.connect(self.create_project)

        layout.addWidget(self.project_name_label)
        layout.addWidget(self.project_name_input)
        layout.addWidget(self.project_code_label)
        layout.addWidget(self.project_code_input)
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_input)
        layout.addWidget(self.end_date_label)
        layout.addWidget(self.end_date_input)
        layout.addWidget(self.thumbnail_label)
        layout.addWidget(self.thumbnail_button)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def choose_thumbnail(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Choose Thumbnail', '', 'Images (*.png *.jpg *.bmp)',
            options=options
        )
        if file_path:
            self.thumbnail_path = file_path
            self.thumbnail_label.setText(f'Project Thumbnail: {file_path}')

    def create_project(self):
        project_name = self.project_name_input.text()
        project_code = self.project_code_input.text()
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()

        # Update config with project name and code
        self.config['pipeline_data']['globals']['project_name'] = project_name
        self.config['pipeline_data']['globals']['project_code'] = project_code
        self.config['pipeline_data']['prjManagement']['ftrack_projectName'] = project_name
        save_config(self.config_file_path, self.config)

        root_path = self.config['root_path']
        ftrack_server_url = self.config['ftrack']['server_url']
        ftrack_api_key = self.config['ftrack']['api_key']
        ftrack_api_user = self.config['ftrack']['api_user']

        # Step 1: Create the project in Ftrack
        self.project, self.session = create_ftrack_project(
            project_name, project_code, start_date, end_date, ftrack_server_url,
            ftrack_api_key, ftrack_api_user
        )

        if not self.project or not self.session:
            QtWidgets.QMessageBox.critical(self, 'Error',
                                            f'Failed to create Ftrack project.')
            return

        # Step 2: Upload the thumbnail to Ftrack
        if self.thumbnail_path:
            try:
                server_location = self.session.query(
                    'Location where name is "ftrack.server"'
                ).one()
                thumbnail_component = self.session.create_component(
                    self.thumbnail_path,
                    {'name': 'thumbnail'},
                    location=server_location
                )
                self.project.create_thumbnail(self.thumbnail_path)
                self.session.commit()

                logger.info(f"Thumbnail uploaded: {self.thumbnail_path}")
            except Exception as e:
                logger.error(f"Error uploading thumbnail: {e}")

        # Step 3: Create initial entities in Ftrack
        initial_entities = self.config['initial_entities']
        for entity in initial_entities:
            if entity['parent_id'] == 'project_id':
                entity['parent_id'] = self.project['id']

        created_entities, asset_versions = create_ftrack_entities(
            self.session, self.project["id"], initial_entities
        )

        if not created_entities:
            QtWidgets.QMessageBox.critical(self, 'Error',
                                          f'Failed to create initial Ftrack entities.')
            return

        logger.info("Created initial entities: %s", created_entities)

        # Step 4: Set up the folder structure in Prism
        project_path = create_prism_project(root_path, project_name,
                                            project_code, self.config)

        if not project_path:
            QtWidgets.QMessageBox.critical(self, 'Error',
                                            f'Failed to create Prism project.')
            return

        # Step 5: Convert and save the thumbnail as project.jpg in the 00_Pipeline folder
        try:
            # Create default thumbnail if none provided
            if not self.thumbnail_path:
                # Create a default colored background
                default_size = (512, 512)
                default_color = (200, 200, 200)  # Light gray
                default_image = Image.new('RGB', default_size, default_color)
            else:
                default_image = Image.open(self.thumbnail_path)
                
            # Process the image
            thumbnail_image = default_image
            if thumbnail_image.mode in ('RGBA', 'LA'):
                background = Image.new(thumbnail_image.mode[:-1],
                                     thumbnail_image.size, (255, 255, 255))
                background.paste(thumbnail_image, thumbnail_image.split()[-1])
                thumbnail_image = background.convert('RGB')
            else:
                thumbnail_image = thumbnail_image.convert('RGB')
            
            # Resize while maintaining aspect ratio
            max_size = (512, 512)
            thumbnail_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save in all required Prism locations
            thumbnail_save_paths = [
                os.path.join(project_path, "00_Pipeline", "project.jpg"),
                os.path.join(project_path, "00_Pipeline", "thumbnail.jpg"),
                os.path.join(project_path, "00_Pipeline", "preview.jpg")
            ]
            
            for save_path in thumbnail_save_paths:
                save_dir = os.path.dirname(save_path)
                os.makedirs(save_dir, exist_ok=True)
                thumbnail_image.save(save_path, "JPEG", quality=95)
                logger.info(f"Thumbnail saved at {save_path}")
                
        except Exception as e:
            logger.error(f"Error saving thumbnail: {e}")
            # Continue execution even if thumbnail processing fails
            pass

        QtWidgets.QMessageBox.information(self, 'Success',
                                          f'Project {project_name} setup complete.')


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ProjectSetupApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
