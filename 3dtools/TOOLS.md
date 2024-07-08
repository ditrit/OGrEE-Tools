# Tools GUI

Now it's possible to use multiple tools on the same GUI.

## Setup

In 3dtools repository:
```
poetry install
poetry shell
python main.py --gui
```

Tools *Converter* and *NonSquareRooms* are installed as packages by poetry. Both projects have specific *pyproject.toml* in their repositories. For now *Converter* in installed for windows. For Linux, change the wheel path in *Converter/pyproject.toml*.

## The GUI

There are two tabs in the GUI for now, one for 3dtools and one for NonSquareRooms. By default 3dtools is loaded with default parameters.
