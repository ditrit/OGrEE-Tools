import sys
import platform

required_version = (3,10) # Or higher
if tuple(map(int,platform.python_version_tuple())) <= required_version:
    print("Please use python 3.10 or higher, aborting.")
    sys.exit(1)

import os
import subprocess
import venv
import shutil
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import distutils.sysconfig

def Print(str):
    print(f'\033[96m{str}\033[0m')

def PrintError(str):
    print(f'\033[91m{str}\033[0m')

setupDir = os.path.dirname(__file__)
rootDir = os.path.realpath(f"{setupDir}/../../")
envDir = f"{rootDir}/.venv"

# Activate the virtual environment
if sys.platform.startswith('win'):  # Windows
    os.system("color") #To output pretty colors
    pythonExe = f"{envDir}\\Scripts\\python.exe"
    wheel = "fbx-2020.3.4-cp310-none-win_amd64.whl"
else:  # Unix/Linux/Mac
    pythonExe = f"{envDir}/bin/python"
    wheel = "fbx-2020.3.4-cp310-cp310-manylinux1_x86_64.whl"

# Create a virtual environment
Print("Creating virtual environment...")
venv.create(envDir, with_pip=True)

# Install the modules in the virtual environment
Print("Installing required packages...")
subprocess.run([pythonExe , '-m', 'pip', 'install', '-r', f'{setupDir}/requirements.txt',])
subprocess.run([pythonExe , '-m', 'pip', 'install', f'{setupDir}/{wheel}'])

packageDir = os.path.realpath(distutils.sysconfig.get_python_lib(prefix=envDir))
Print(f"Copying {setupDir}/FbxCommon.py to {packageDir}...")
shutil.copy2(f"{setupDir}/FbxCommon.py",packageDir)

print('\033[92mDone !\033[0m')