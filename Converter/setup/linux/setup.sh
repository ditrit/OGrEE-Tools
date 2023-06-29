#!/bin/bash

# Define color codes
CYAN='\e[0;96m'
RED='\033[0;91m'
NC='\033[0m' # No Color

Print() {
	echo -e "${CYAN}$1${NC}"
}

PrintError() {
	echo -e "${RED}$1${NC}"
}

if [[ "$0" == "$BASH_SOURCE" ]]; then
	PrintError "You need to source this script, using '.' or 'source' : source Converter/setup/linux/setup.sh"
	exit 1
fi

script=$(realpath "${BASH_SOURCE[-1]}")
scriptPath=$(dirname "$script")
rootDir=$(realpath $scriptPath/../../..)

Print "Creating virtual env at $rootDir\.venv..."
python3.10 -m venv $rootDir/.venv
if [ $? -ne 0 ]; then
	PrintError "Error while creating virtual env."
	return 1
fi

Print "Activating virtual env..."
source $rootDir/.venv/bin/activate
if [[ $? -ne 0 ]] || [[ -z "$VIRTUAL_ENV" ]]; then
	PrintError "Error while activating virtual env"
	return 1
fi

Print "Installing requirements..."
python -m pip install -r $scriptPath/../requirements.txt
if [ $? -ne 0 ]; then
	PrintError "Error while installing requirements, check if $(realpath $scriptPath/../requirements.txt) exists and is correctly configured."
	return 1
fi

python -m pip install $scriptPath/fbx-2020.3.4-cp310-cp310-manylinux1_x86_64.whl
if [ $? -ne 0 ]; then
	PrintError "Error while installing requirements, check if $(realpath $scriptPath/fbx-2020.3.4-cp310-cp310-manylinux1_x86_64.whl) exists and is for python 3.10."
	return 1
fi

packageDir=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

Print "Adding $(realpath $scriptPath/../FbxCommon.py) to $packageDir..."
cp $scriptPath/../FbxCommon.py $packageDir
if [ $? -ne 0 ]; then
	PrintError "Error while moving FbxCommon.py, check if the file is present at $(realpath $scriptPath/..)"
	return 1
fi

Print "Adding $rootDir to python path..."
echo $rootDir >$packageDir/OGrEE-Tools.pth
if [ $? -ne 0 ]; then
	PrintError "Error while writing $packageDir/OGrEE-Tools.pth"
	return 1
fi

Print "\n########################################################################################################################\n\nVirtual environment configured. To exit, type \"deactivate\". To 	enter again, type \". .venv/bin/activate\".\n"
