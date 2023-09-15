import sys
import platform

def Print(str):
    print(f'\033[96m{str}\033[0m')

def PrintError(str):
    print(f'\033[91m{str}\033[0m')

required_version = (3,10) # Only
if tuple(map(int,platform.python_version_tuple()))[:2] != required_version:
    PrintError("Please use python 3.10, aborting.")
    sys.exit(1)

import os
import subprocess
import venv
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import distutils.sysconfig

setupDir = os.path.dirname(__file__)
rootDir = os.path.realpath(f"{setupDir}/../../")
envDir = os.path.realpath(f"{rootDir}/.venv")

if sys.platform.startswith('win'):  # Windows
    os.system("color") #To output pretty colors
    pythonExe = f"{envDir}\\Scripts\\python.exe"
    venvActivationCommand = f".venv\\Script\\activate"
else:  # Unix/Linux/Mac
    pythonExe = f"{envDir}/bin/python"
    venvActivationCommand = f". .venv/bin/activate"

Print("Creating virtual environment...")
venv.create(envDir, with_pip=True)

# Install the modules in the virtual environment
Print("Installing required packages...")
try:
    subprocess.run([pythonExe , '-m', 'pip', 'install', '-r', f'{setupDir}/requirements.txt',])
except Exception as e:
    PrintError(f"Error while installing requirements, check if {setupDir}/requirements.txt exists and is correctly configured.")
    raise e

packageDir = os.path.realpath(distutils.sysconfig.get_python_lib(prefix=envDir))

Print(f"Adding {rootDir} to python path...")
try:
    pth = open(f"{packageDir}/OGrEE-Tools.pth","w")
    pth.write(rootDir)
    pth.close()
except Exception as e:
    PrintError(f"Error while writing {packageDir}/OGrEE-Tools.pth")
    raise e

print(f'\033[92mDone ! You can start the virtual environment by typing "{venvActivationCommand}" from {rootDir}. To deactivate it, just type "deactivate" from anywhere\033[0m')
