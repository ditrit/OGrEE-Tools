#!/usr/bin/env bash

# Check Python version
if ! python3 -c 'import sys; assert sys.version_info >= (3,7)' > /dev/null; then
    echo "Error: Python version 3.7 or higher is required."
    exit 1
else
    echo "Python version is compatible. Proceeding with installations."
fi

# OGrEE-Tools/3dtools installation
pip3 install -r ./requirements.txt

# YOLOV5 installation
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip3 install -r ./requirements.txt
