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

# 3dtools
Veuillez lire attentivement les instructions suivantes pour modifier le rectangle AVANT de cliquer sur le bouton « Modifier des rectengles » :

a. Après avoir cliqué sur le bouton « Modifier des rectengles », une nouvelle fenêtre sera générée et le texte dans le coin supérieur gauche de cette fenêtre indiquera que vous êtes en « create mode ». Ce mode est en cours d'amélioration et certaines opérations peuvent provoquer un crash du programme. Lorsque vous êtes en « create mode », veuillez double-cliquer sur une bordure rectangulaire pour entrer en « modify mode », ou appuyez sur ESC pour quitter, veuillez ne pas effectuer d'autres opérations.

b. Si vous souhaitez ajuster un rectangle, veuillez d'abord double-cliquer sur n'importe quel côté du rectangle que vous souhaitez ajuster, et vous entrerez en « modify mode ». La position et la taille du rectangle ne peuvent être ajustées que si nous passons en « modify mode ».

c. Si vous souhaitez ajuster la position d'un certain rectangle, veuillez d'abord entrer dans « modify mode ». Appuyez ensuite et maintenez un côté du rectangle avec le bouton gauche de la souris, puis déplacez la souris pour modifier la position du rectangle.

d. Si vous souhaitez redimensionner un rectangle, veuillez d'abord entrer dans « modify mode ». Appuyez ensuite et maintenez un coin du rectangle avec le bouton gauche de la souris, puis déplacez la souris pour modifier la taille du rectangle.

e. Lorsque vous pensez avoir terminé d'ajuster un certain rectangle, vous pouvez cliquer avec le bouton droit n'importe où pour quitter « modify mode ».

f. Lorsque vous pensez avoir terminé d'ajuster tous les rectangles, vous pouvez appuyer sur la touche ESC pour enregistrer les modifications apportées au fichier json et fermer la fenêtre d'image. Vous ne pourrez peut-être pas fermer une fenêtre en appuyant sur la croix dans le coin supérieur droit de la fenêtre, et lorsque vous appuyez sur ESC, vos modifications apportées au json seront automatiquement enregistrées.
