import PyInstaller.__main__
import sys
import os
from pathlib import Path

# Update icon path handling to ensure it exists
icon_path = Path('src/assets/Logo_white.ico')
if not icon_path.exists():
    print(f"Warning: Icon file not found at {icon_path}")
    sys.exit(1)

# Determine OS-specific settings
is_windows = sys.platform.startswith('win')
separator = ';' if is_windows else ':'
icon_flag = f'--icon={icon_path.absolute()}'

# Define data paths with OS-appropriate separators
data_paths = [
    f'src/assets/*{separator}assets',
    f'src/ui{separator}ui',
    f'src/collectors{separator}collectors',
    f'src/analysis{separator}analysis',
    f'src/utils{separator}utils',
    f'src/generation{separator}generation',
]

# Base configuration
pyinstaller_args = [
    'src/reddit_analyzer_app.py',
    '--name=RedditAnalyzer',
    '--onefile',
    '--windowed',
    '--paths=src',
    '--clean',
    '--noconfirm',
]

# Add data paths
for data_path in data_paths:
    pyinstaller_args.append(f'--add-data={data_path}')

# Add hidden imports
hidden_imports = [
    'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 
    'PySide6.QtSvg', 'PySide6.QtNetwork',
    'utils', 'analysis', 'collectors', 'ui', 'generation',
    'praw', 'pandas', 'numpy', 'nltk',
    'matplotlib', 'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_qt5', 'seaborn',
    'vaderSentiment.vaderSentiment', 'sklearn', 'scipy',
    'torch', 'diffusers', 'transformers',
    'signal', 'threading', 'asyncio', 'concurrent.futures'
]

for imp in hidden_imports:
    pyinstaller_args.append(f'--hidden-import={imp}')

# Add collect-submodules
collect_submodules = ['collectors', 'analysis']
for module in collect_submodules:
    pyinstaller_args.append(f'--collect-submodules={module}')

# Add collect-all packages
collect_all = [
    'praw', 'prawcore', 'matplotlib', 'seaborn', 'numpy',
    'pandas', 'nltk', 'vaderSentiment', 'sklearn', 'scipy',
    'PySide6', 'textblob', 'torch', 'diffusers', 'transformers',
    'PIL', 'bs4', 'requests', 'wordcloud'
]

for package in collect_all:
    pyinstaller_args.append(f'--collect-all={package}')

# Add icon
pyinstaller_args.append(icon_flag)

try:
    print("Starting PyInstaller build process...")
    print(f"Building for {'Windows' if is_windows else 'macOS'}")
    PyInstaller.__main__.run(pyinstaller_args)
    print("Build process completed successfully!")
except Exception as e:
    print(f"Error during PyInstaller execution: {e}")
    print(f"Current working directory: {os.getcwd()}")
    sys.exit(1)
