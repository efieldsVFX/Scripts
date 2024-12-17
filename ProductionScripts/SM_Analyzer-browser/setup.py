from setuptools import setup, find_packages

setup(
    name="sm_analyzer",
    version="1.0",
    packages=find_packages(),
    author="Eric Fields",
    author_email="efieldsvfx@gmail.com",
    description="Social Media Analyzer for analyzing social media data",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/efieldsvfx/SM_Analyzer",
    install_requires=[
        'pandas',
        'numpy',
        'nltk',
        'textblob',
        'wordcloud',
        'matplotlib',
        'seaborn',
        'streamlit',
        'tweepy',
        'python-dotenv'
    ],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)