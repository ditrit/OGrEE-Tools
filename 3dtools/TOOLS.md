# Tools GUI

Now it's possible to use multiple tools on the same GUI.

Supported tools are 3dtools, NonSquareRooms and FBX.

## Setup

In 3dtools repository:
```
pip install poetry  # if you do not have poetry
poetry install
poetry env use <PATH_TO_PYTHON_3.10>  # Python 3.10 is mandatory for this project
poetry shell
python main.py --gui
```

Tools *Converter*, *NonSquareRooms* and *FBX* are installed as packages by poetry. All these subprojects have specific *pyproject.toml* in their repositories. For now *Converter* in installed for windows. For Linux, change the wheel path in *Converter/pyproject.toml*.

## The GUI

There are three tabs in the GUI for now, one for 3dtools, one for NonSquareRooms and one for FBX. By default 3dtools is loaded with default parameters.

### 3dtools tab

![alt text](https://github.com/ditrit/OGrEE-Tools/blob/all-tools-gui/3dtools/doc/tools_3dtools.png)

### NonSquareRooms tab

![alt_text](https://github.com/ditrit/OGrEE-Tools/blob/all-tools-gui/3dtools/doc/tools_nsr.png)

### FBX tab

![alt_text](https://github.com/ditrit/OGrEE-Tools/blob/all-tools-gui/3dtools/doc/tools_fbx.png)


