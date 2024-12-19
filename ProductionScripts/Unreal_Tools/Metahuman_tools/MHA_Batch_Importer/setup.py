"""Setup configuration for MHA Batch Importer."""

from setuptools import find_packages, setup

setup(
    name="mha_batch_importer",
    version="1.0.0",
    description="Batch MetaHuman Asset Importer for Unreal Engine",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "ftrack-python-api>=2.0.0",
        "python-dotenv>=1.0.0",
        "PySide6>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pre-commit",
            "black",
            "flake8",
            "flake8-docstrings",
            "isort",
        ]
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mha-importer=mha_batch_importer.run:main",
        ],
    },
) 