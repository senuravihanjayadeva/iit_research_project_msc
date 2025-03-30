#!/bin/bash

# Install dependencies
pip install torch torchvision torchaudio

# Install Detectron2 from source (for compatibility)
pip install 'git+https://github.com/facebookresearch/detectron2.git'

# Verify installation
python -c "import detectron2; print('Detectron2 installed successfully')"
