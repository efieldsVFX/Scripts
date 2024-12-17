#!/bin/bash

echo "Starting Social Media Analytics Dashboard..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.8 or higher from https://www.python.org/downloads/"
    echo "Or use: brew install python3"
    read -p "Press enter to exit"
    exit 1
fi

# Check if virtual environment exists, create if it doesn't
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please make sure you have venv installed."
        read -p "Press enter to exit"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    read -p "Press enter to exit"
    exit 1
fi

# Upgrade pip to latest version
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install wheel and setuptools first
echo "Installing base dependencies..."
pip install wheel setuptools

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Please check your internet connection and try again."
    read -p "Press enter to exit"
    exit 1
fi

# Download spaCy model
echo "Downloading spaCy model..."
python3 -m spacy download en_core_web_sm

# Start the dashboard
echo "Starting the dashboard..."
cd src
streamlit run dashboard.py

# Deactivate virtual environment when done
deactivate
