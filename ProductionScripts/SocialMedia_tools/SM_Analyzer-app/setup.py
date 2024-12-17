from setuptools import setup, find_packages

setup(
    name="social-media-analyzer",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'nltk',
        'textblob',
        'wordcloud',
        'matplotlib',
        'seaborn',
        'transformers',
        'torch'
    ],
    entry_points={
        'console_scripts': [
            'social-media-analyzer=your_main_module:main',  # Replace with your actual entry point
        ],
    },
) 