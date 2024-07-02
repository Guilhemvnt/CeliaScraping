#!/bin/bash

echo "Step 1: Creating a virtual environment named 'venv'..."
python3 -m venv venv

echo "Step 2: Activating the virtual environment..."
source venv/bin/activate

echo "Step 3: Installing packages from requirements.txt..."
pip install -r requirements.txt

echo "Installed packages:"
pip list

echo "Setup complete. The virtual environment 'venv' is ready to use."
