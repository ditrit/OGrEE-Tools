# How to use
Launch the GUI.py file by going into the ToolBox folder and using in your terminal "python Gui.py".
When you launch the ToolBox choose the tools that you want to use and your own directory of OGrEE-Tools to setup the root directory of the ToolBox.

# Principal window

After you have launched ToolBox you can choose on the top left corner which tools you want to use.
You also have on the bottom a bar in which will be written the code line created by the tool you use and a terminal. The button next to the terminal is used to launch this command into your computer's terminal.

# FBX Converter

To create your FBX Converter command you will need some mandatory items :
- PNG : choose your PNGs with the first "parcourir" button. It will open a new window with a treeview to navigate through your files and find your PNGs. If the folder open contains PNGs they will be displayed and you will be able to choose one by clicking on it. Then you can choose the corresponding face of your 3D model and click on "Ajouter" to add this PNG to the list of those you want to use. If the file open is a PNG, it will only display it and it will be automaticaly selected, no need to click on it. Once you've choosen all the faces you want press "Valider".
- Dimensions : There are two way to choose your 3D model dimensions. First, manually in cm. Secondly, by choosing a JSON file containing dimensions.
- Out path : Browse through your file to define where you want your FBX file to end.

Optional item :
- Name : You can choose the name that you want to give your FBX file.

Once all the mandatory items are provided you will be able to generate to command line.

# NonSquareRooms

To get your Json file completed and giving you a disposition of each tiles adapted to your room, you need to provide the Json file containing the configuration of your room. After that you can select several parameters: the name of your final Json file, the offset that you want for your installation, the size of the tiles and the angle that you want your tiles to have. If you don't fill those informations the program will take the following parameters: name="name_of_your_file-tiles" , Tile Size=60 cm, Offset=(0,0), angle=0°.
Now, you can choose if you want to draw the room or optimize the tiling of the room by selected those buttons.
Clicking on the "generate" button will give you the command line that you will execute by clicking on the "enter" button to get your final file.

