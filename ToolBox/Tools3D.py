
import tkinter as tk
import subprocess
from tkinter import filedialog
import os
import cv2
import numpy as np
import json
import random

#variables globales
drawing = False
select = False
initial_x,initial_y = -1,-1
final_x,final_y = -1,-1
ix,iy = -1,-1
left_x,up_y = -1,-1
right_x,down_y = -1,-1
data_set = []
select_data = [-1, -1, -1, -1]
k = 0
point_resize = False
side_move = False
code = 1
named = ['']*len(data_set)


def create_3DT(self):
        self.frame = tk.Frame(self.root, width=200, height=100, bg="light grey")
        self.frame.pack_propagate(False)

#Etape01(I. Etape pour générer json) est pour geneter le fichier json. Après finir Etape01, on a Etape02 pour modifier le fichier json.
#Créez des zones de texte pour les paramètres modifiables par l'utilisateur
        label00 = tk.Label(self.frame, text="I. Etape pour générer json :", bg="light grey", anchor="w", font=("Times New Roman", 10, "bold"))
        label00.grid(row=0, column=0, ipady=10, sticky='w')
        label01 = tk.Label(self.frame, text="Servername :", bg="light grey", anchor="w")
        label01.grid(row=1,column=0, ipady=5, sticky='w')
        label02 = tk.Label(self.frame, text="Height :", bg="light grey", anchor="w")
        label02.grid(row=2,column=0, ipady=5, sticky='w')
        label03 = tk.Label(self.frame, text="Length :", bg="light grey", anchor="w")
        label03.grid(row=3,column=0, ipady=5, sticky='w')
        label04 = tk.Label(self.frame, text="Type(entrez rear ou front) :", bg="light grey", anchor="w")
        label04.grid(row=4,column=0, ipady=5, sticky='w')

# Créez des zones de saisie pour les paramètres modifiables par l'utilisateur
        entry01 = tk.Entry(self.frame, width=100, justify='left')
        entry01.grid(row=1,column=2, ipady=5, sticky='w')
        entry01.insert(0, 'Cliquez sur le bouton « Choisir une image » pour importer le chemin de image')
        entry02 = tk.Entry(self.frame)
        entry02.grid(row=2, column=1, ipady=5, sticky='w')
        entry02.insert(0, '86.8')
        entry03 = tk.Entry(self.frame)
        entry03.grid(row=3, column=1, ipady=5, sticky='w')
        entry03.insert(0, '482.4')
        entry04 = tk.Entry(self.frame)
        entry04.grid(row=4, column=1, ipady=5, sticky='w')
        entry04.insert(0, 'front')

#Créer un bouton pour lire l'image à traiter
        def choisir_png():
            global img, h, w, _,scale_percent,width,height,dim,image,thickness, mask, screen,rows,cols
            file_path = filedialog.askopenfilename(title="Choisir une image")
            entry01.delete(0, tk.END)
            entry01.insert(0, file_path)
            # Chemin des images
            img = cv2.imread(file_path)
            h, w, _ = img.shape
            scale_percent = 30  # percent of original size
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            image = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
            thickness = 3

            mask = np.zeros(image.shape, np.uint8)
            mask[:] = 255
            # cv2.rectangle(mask, (initial_x, initial_y), (final_x, final_y),(0, 0, 0),2)
            screen = cv2.bitwise_and(image, mask)
            rows = len(data_set)
            cols = 3

        btn_choisir_png = tk.Button(self.frame, text='Choisir une image', command=choisir_png, width=20)
        btn_choisir_png.grid(row=1, column=1, sticky='w')

#Créer un bouton pour générer le fichier json de l'image spécifiée par l'utilisateur
        def Etape01():
                # Récupérer les paramètres saisis par l'utilisateur
                ser = entry01.get()
                H = entry02.get()
                L = entry03.get()
                Type = entry04.get()
                #Assemblez l'instruction qui sera envoyée au terminal pour exécuter main.py dans le dossier 3dtools.
                python_command = f"python main.py --servername {ser} --height {H} --width {L} --face {Type}"
                #Allez dans le dossier 3dtools pour exécuter main.py.
                os.chdir("..")
                os.chdir("3dtools")
                #Exécuter main.py.
                with subprocess.Popen(python_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      shell=True) as process:
                        # Envoyer "15" puis "finish" comme "input", pour que main.py puisse terminer.
                        process.communicate(input=b"15\nfinish\n")
        #Ce bouton pour exécuter main.py.
        btn01 = tk.Button(self.frame,text='Démarrer generer json', command=Etape01, width=20)
        btn01.grid(row=5, column=1, sticky='w')

#Ce qui suit est Etape02(II. Etape pour modifier des rectangles), qui est pour creer une fenetre dans laquelle on peut modifier des rectangle
        labelétape02 = tk.Label(self.frame, text="II. Etape pour modifier des rectangles :", bg="light grey", anchor="w", font=("Times New Roman", 10, "bold"))
        labelétape02.grid(row=6, column=0, ipady=10, sticky='w')
#Créer un bouton pour choisir le json à modifier
        labelchoisirjson = tk.Label(self.frame, text="Choisir un json :", bg="light grey", anchor="w")
        labelchoisirjson.grid(row=7, column=0, ipady=5, sticky='w')
        entrychoisirjson = tk.Entry(self.frame, width=100, justify='left')
        entrychoisirjson.insert(0, 'Afin de ajuster le rectangle, la sélection de json et de image est nécessaire.')
        entrychoisirjson.grid(row=7, column=2, ipady=5, sticky='w')

        def choisir_json():
            global color, json_data,file_path_json,code
            file_path_json = filedialog.askopenfilename(title="Le chemin de json")
            entrychoisirjson.delete(0, tk.END)
            entrychoisirjson.insert(0, file_path_json)
            #importer json data
            with open(
                    file_path_json,
                    'r', encoding='utf8') as fp:
                json_data = json.load(fp)
            # rect = []
            for i in json_data:
                xl = i["elemPos"][0] / 482.4 * image.shape[1]  # i["elemPos"][0]
                yl = (86.8 - i["elemPos"][2]) / 86.8 * image.shape[0]  # i["elemPos"][2]
                xp = i["elemSize"][0] / 482.4 * image.shape[1]  # i["elemSize"][0]
                yp = i["elemSize"][2] / 86.8 * image.shape[0]  # i["elemSize"][2]
                xr = xl + xp
                yh = yl - yp
                xL = int(xl)
                xR = int(xr)
                yL = int(yl)
                yH = int(yh)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                data_set.append((xL, yH, xR, yL, code))
                named.append(i["location"])
                code = code + 1

        btn_choisir_json = tk.Button(self.frame, text='Choisir un json', command=choisir_json, width=20)
        btn_choisir_json.grid(row=7, column=1, sticky='w')

# Vous trouverez ci-dessous les instructions pour modifier un rectangle.
        labelchoisirjson = tk.Label(self.frame, text="Veuillez lire attentivement les instructions suivantes pour modifier le rectangle AVANT de cliquer sur le bouton « Modifier des rectengles » :", bg="light grey", anchor="w")
        labelchoisirjson.grid(row=8, column=0, columnspan=5, ipady=5, sticky='w')
        labelinsta = tk.Label(self.frame,
                              text="a. Après avoir cliqué sur le bouton « Modifier des rectengles », une nouvelle fenêtre sera générée et le texte dans le coin supérieur gauche de cette fenêtre indiquera que vous êtes en « create mode ». Ce mode est en cours d'amélioration et certaines opérations peuvent provoquer un crash du programme. Lorsque vous êtes en « create mode », veuillez double-cliquer sur une bordure rectangulaire pour entrer en « modify mode », ou appuyez sur ESC pour quitter, veuillez ne pas effectuer d'autres opérations.",
                              fg="red", bg="light grey", anchor="w", wraplength=800, justify="left")
        labelinsta.grid(row=9, column=0, columnspan=5, ipady=5, sticky='w')
        labelinstb= tk.Label(self.frame,
                             text="b. Si vous souhaitez ajuster un rectangle, veuillez d'abord double-cliquer sur n'importe quel côté du rectangle que vous souhaitez ajuster, et vous entrerez en « modify mode ». La position et la taille du rectangle ne peuvent être ajustées que si nous passons en « modify mode ».",
                             bg="light grey", anchor="w", wraplength=800, justify="left")
        labelinstb.grid(row=10, column=0, columnspan=5, ipady=5, sticky='w')
        labelinstc = tk.Label(self.frame,
                              text="c. Si vous souhaitez ajuster la position d'un certain rectangle, veuillez d'abord entrer dans « modify mode ». Appuyez ensuite et maintenez un côté du rectangle avec le bouton gauche de la souris, puis déplacez la souris pour modifier la position du rectangle.",
                              bg="light grey", anchor="w", wraplength=800, justify="left")
        labelinstc.grid(row=11, column=0, columnspan=5, ipady=5, sticky='w')
        labelinstd = tk.Label(self.frame,
                              text="d. Si vous souhaitez redimensionner un rectangle, veuillez d'abord entrer dans « modify mode ». Appuyez ensuite et maintenez un coin du rectangle avec le bouton gauche de la souris, puis déplacez la souris pour modifier la taille du rectangle.",
                              bg="light grey", anchor="w", wraplength=800, justify="left")
        labelinstd.grid(row=12, column=0, columnspan=5, ipady=5, sticky='w')
        labelinste = tk.Label(self.frame,
                              text="e. Lorsque vous pensez avoir terminé d'ajuster un certain rectangle, vous pouvez cliquer avec le bouton droit n'importe où pour quitter « modify mode ».",
                              bg="light grey", anchor="w", wraplength=800, justify="left")
        labelinste.grid(row=13, column=0, columnspan=5, ipady=5, sticky='w')
        labelinstf = tk.Label(self.frame,
                              text="f. Lorsque vous pensez avoir terminé d'ajuster tous les rectangles, vous pouvez appuyer sur la touche ESC pour enregistrer les modifications apportées au fichier json et fermer la fenêtre d'image. Vous ne pourrez peut-être pas fermer une fenêtre en appuyant sur la croix dans le coin supérieur droit de la fenêtre, et lorsque vous appuyez sur ESC, vos modifications apportées au json seront automatiquement enregistrées.",
                              bg="light grey", anchor="w", wraplength=800, justify="left")
        labelinstf.grid(row=14, column=0, columnspan=5, ipady=5, sticky='w')

#Ensuite, un autre script appelé "modifier.py" sera appelé pour générer une nouvelle fenêtre dans laquelle tous les rectangles seront affichés et l'utilisateur pourra ajuster tous les rectangles.

        # Définir la fonction callback de la souris, dessiner et modifier un rectangle
        def modify_rectangle(event, x, y, flags, param):
            global initial_x, initial_y, final_x, final_y, ix, iy, left_x, up_y, right_x, down_y
            global data_set, select_data, code, k
            global drawing, select, point_resize, side_move
            if event == cv2.EVENT_LBUTTONDOWN and drawing == False and select == False:
                drawing = True
                initial_x = x
                initial_y = y
            elif event == cv2.EVENT_MOUSEMOVE and drawing == True:
                final_x = x
                final_y = y
            elif event == cv2.EVENT_LBUTTONDOWN and drawing == True:
                drawing = False
                code = k + 1
                name = "Frame " + str(code)
                final_x = x
                final_y = y
                # cv2.rectangle(img, (initial_x, initial_y), (final_x, final_y),(0, 0, 0),2)
                cv2.putText(img, name, (initial_x - 3, initial_y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)
                data_set.append((initial_x, initial_y, x, y, code))
                k = k + 1
                #print("i=", i)
            elif event == cv2.EVENT_LBUTTONDBLCLK and select == False:
                select = True
                drawing = False
                initial_x, initial_y = -1, -1
                final_x, final_y = -1, -1
                for n in range(len(data_set)):
                    (left_x, right_x) = sorted((data_set[n][0], data_set[n][2]))
                    (up_y, down_y) = sorted((data_set[n][1], data_set[n][3]))
                    # Détermine si la position du double-clic est la ligne supérieure ou inférieure de la rectangle de destination
                    if (left_x - 3 <= x and x <= right_x + 3):
                        if (up_y - 3 <= y and y <= up_y + 3) or (down_y - 3 <= y and y <= down_y + 3):
                            select_data = data_set[n]
                            code = data_set[n][4]
                            break
                    # Détermine si la position du double-clic est la ligne gauche ou droite de la rectangle de destination
                    if (up_y - 3 <= y and y <= down_y + 3):
                        if (left_x - 3 <= x and x <= left_x + 3) or (right_x - 3 <= x and x <= right_x + 3):
                            select_data = data_set[n]
                            code = data_set[n][4]
                            break
                # name = "Frame " + str(code) + "activate"
                # cv2.putText(mask, name, (3, 3), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)
                print("select_data=", select_data)
            elif event == cv2.EVENT_RBUTTONDOWN and select == True:
                select = False
                # name = "disactivate"
                # cv2.putText(img, name, ( 3, 3), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
            elif event == cv2.EVENT_LBUTTONDOWN and select == True and drawing == False:
                ix = x
                iy = y
                # Déterminer quel point ou côté est choisi
                (left_x, right_x) = sorted((select_data[0], select_data[2]))
                (up_y, down_y) = sorted((select_data[1], select_data[3]))
                # C'est le point qui est choisi
                if (left_x - 3 <= x and x <= left_x + 3) or (right_x - 3 <= x and x <= right_x + 3):
                    if (up_y - 3 <= y and y <= up_y + 3) or (down_y - 3 <= y and y <= down_y + 3):
                        point_resize = True
                        # Confirmé le point à opérer
                        if (left_x - 3 <= x and x <= left_x + 3):
                            final_x = left_x
                            initial_x = right_x
                        if (right_x - 3 <= x and x <= right_x + 3):
                            final_x = right_x
                            initial_x = left_x
                        if (up_y - 3 <= y and y <= up_y + 3):
                            final_y = up_y
                            initial_y = down_y
                        if (down_y - 3 <= y and y <= down_y + 3):
                            final_y = down_y
                            initial_y = up_y
                # C'est le coté qui est choisi
                if (left_x + 3 < x and x < right_x - 3) or (up_y + 3 < y and y < down_y - 3):
                    if (left_x - 3 < x and x < left_x + 3) or (right_x - 3 < x and x < right_x + 3):
                        side_move = True
                    if (up_y - 3 < y and y < up_y + 3) or (down_y - 3 < y and y < down_y + 3):
                        side_move = True
                # named[code - 1] = "Frame " + str(code) + " - Updated"
            # Zoom
            elif event == cv2.EVENT_MOUSEMOVE and point_resize == True:
                final_x = x
                final_y = y
                select_data = (initial_x, initial_y, final_x, final_y, code)
            # Mouvement
            elif event == cv2.EVENT_MOUSEMOVE and side_move == True:
                dx = x - ix
                dy = y - iy
                initial_x = left_x + dx
                final_x = right_x + dx
                initial_y = up_y + dy
                final_y = down_y + dy
                select_data = (initial_x, initial_y, final_x, final_y, code)
            # Terminer
            elif event == cv2.EVENT_LBUTTONUP and select == True:
                point_resize = False
                side_move = False
                for idx, rect in enumerate(data_set):
                    if rect[4] == code:
                        del data_set[idx]
                        global namet
                        namet = named[idx]
                        del named[idx]
                        break
                data_set.append(select_data[:])
                named.append(namet)

        def Etape02():
            global Width,Height,elemPos,elemSize
            Width = float(entry02.get())
            Height = float(entry03.get())
            # Créer des fenêtres et lier des fonctions aux fenêtres
            cv2.namedWindow("Window")
            # Connecter le bouton de la souris à la fonction callback
            cv2.setMouseCallback("Window", modify_rectangle)
            elemPos = [[0, 0, 0] for _ in range(len(data_set))]
            elemSize = [[0, 0, 0] for _ in range(len(data_set))]
            while True:
                # Effacer les traces rectangulaires précédentes
                mask[:] = 255
                cv2.rectangle(mask, (initial_x, initial_y), (final_x, final_y), (0, 0, 0), 2)

                # Dessinez tous les rectangles
                for n in range(len(data_set)):
                    cv2.rectangle(mask, (data_set[n][0], data_set[n][1]), (data_set[n][2], data_set[n][3]), (0, 0, 255),
                                  lineType=cv2.LINE_4, thickness=2)
                    cv2.putText(mask, named[n], (data_set[n][0], data_set[n][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 255), 1)

                # S’il y a un rectangle sélectionné, dessinez le rectangle sélectionné
                if select:
                    cv2.rectangle(mask, (select_data[0], select_data[1]), (select_data[2], select_data[3]), (255, 0, 0),
                                  2)
                    cv2.putText(mask, named[n], (data_set[n][0], data_set[n][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 0, 0), 1)
                    # Afficher "activate" dans le coin supérieur gauche de la fenêtre
                    cv2.putText(mask, "modify mode", (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                else:
                    # Afficher "activer" dans le coin supérieur gauche de la fenêtre
                    cv2.putText(mask, "create mode", (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                # Mettre à jour l’écran
                screen = cv2.bitwise_and(image, mask)
                # Afficher la fenêtre
                cv2.imshow("Window", screen)

                # Attendez l’opération de la touche de l’utilisateur. Si c’est la touche ESC (code ASCII 27), quittez la boucle puis renvoye les données modifier à document json.
                key = cv2.waitKey(10)
                if key == 27:
                    for q in range(len(data_set)):
                        if data_set[q][0] <= data_set[q][2]:
                            elemPos[q][0] = data_set[q][0]
                            elemSize[q][0] = data_set[q][2] - data_set[q][0]
                        else:
                            elemPos[q][0] = data_set[q][2]
                            elemSize[q][0] = data_set[q][0] - data_set[q][2]

                        if data_set[q][1] <= data_set[q][3]:
                            elemPos[q][2] = data_set[q][3]
                            elemSize[q][2] = data_set[q][3] - data_set[q][1]
                        else:
                            elemPos[q][2] = data_set[q][1]
                            elemSize[q][2] = data_set[q][1] - data_set[q][3]
                        json_data[q]["elemPos"][0] = elemPos[q][0] / image.shape[1] * Width
                        json_data[q]["elemPos"][2] = Height - elemPos[q][2] / image.shape[0] * Height
                        json_data[q]["elemSize"][0] = elemSize[q][0] / image.shape[1] * Width
                        json_data[q]["elemSize"][2] = elemSize[q][2] / image.shape[0] * Height
                        json_data[q]["location"] = named[q]
                    with open(file_path_json,'w') as fp:
                        json.dump(json_data, fp, indent=4)
                    break
            cv2.destroyAllWindows()

        btn_run_modifier = tk.Button(self.frame, text='Modifier des rectengles', command=Etape02, width=20)
        btn_run_modifier.grid(row=15, column=1, sticky='w')

        return self.frame

