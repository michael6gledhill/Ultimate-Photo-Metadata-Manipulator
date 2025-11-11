#!/bin/bash

echo "=========================================="
echo "Photo Metadata Manipulator - Quick Setup"
echo "=========================================="
echo ""

cd ~/

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install git

sudo port install git

xcode-select --install

git clone https://github.com/michael6gledhill/Ultimate-Photo-Metadata-Manipulator.git

cd Ultimate-Photo-Metadata-Manipulator

./run.sh