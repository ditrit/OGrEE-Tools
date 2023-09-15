# COMPOS GUIDE
## _3d tools for server VR_


COMPOS est un programme de machine learning qui détecte les composants sur le photo de la face du serveur, et exporter la coordonnée, la similarité et la fiche déscription json. Il aide l'ingénieur Unity à créer des modèles 3D de serveur en indiquant les positions des composants en mm. Il peut trouver des interfaces communes, des disques durs, des slots, permetant de accélérer la modélisation 3D.

- Algorithmes variés, du plus simple au plus complexe
- Travailler avec le plus puissant objet detection algorithme YOLOV5
- Boîte à outils puissante

## Catégories prises en charge

| Name | method |
| ------ | ------ |
| idrac | template matching |
| usb | rectangle detect |
| d-sub female/vga | image's feature points |
| d-sub male/rs232 | image's feature points |
| slot normal | YOLOV5 object detection |
| slot lp | YOLOV5 object detection |
| disk lff | YOLOV5 object detection |
| disk sff | YOLOV5 object detection |
| power supply unit | YOLOV5 object detection |

## Méthode
Selon la difficulté de la tâche, le programme utilise différentes méthodes de détection. D'une part, cela devrait être dû au fait que l'ajout de trop de classes à l'algorithme deep learning YOLOV augmentera la difficulté de l'apprentissage, d'autre part, l'exploration de différents algorithmes aidera à fournir des idées pour la détection de la carte mère. Ce qui suit présentera les idées de traitement de chaque cible séparément.  
### idrac
Le porte idrac(porte réseau) a une saillie et 8 longues broches. Il se distingue facilement des autres graphiques. Par conséquent, nous pouvons obtenir un bon taux de réussite en utilisant l'algorithme de correspondance de modèles le plus simple.   
Son principe est de spécifier d'abord le modèle standard, puis d'utiliser le filtre de contour pour obtenir le bord de l'image et le modèle. Enfin, comparez chaque zone de même taille sur l'image avec le modèle, et trouvez le point avec la plus grande similitude locale comme position de l'idrac. Pour trouver tous les orientation, le programme inverse le modèle à 180° et répéter les étaps desur.  
Pour les objets standardisés et spéciaux, la méthode de correspondance des modèles peut rapidement donner des résultats. Il en va de même pour les objets sur la carte mère. Il gère la rotation, mais pas les défis de mise à l'échelle.  

### usb
Usb est une interface série courante, largement utilisée dans divers types de serveurs. La template matching ne fonctionne pas bien ici car elle est si régulière qu'elle est souvent confondue avec les mailles de ventilation et les boutons.    
Usb est un rectangle régulier, on s'attend donc à le déterminer en détectant un rectangle de la bonne taille.    
Le cœur de cette méthode est la transformée de Huff, une méthode pour convertir le bord de l'image du système de coordonnées rectangulaires au système de coordonnées polaires, puis nous pouvons facilement trouver le segment de ligne de la longueur et de l'angle spécifiés. Ensuite, nous parcourons la combinaison de tous les segments de ligne pour déterminer s'ils forment le rectangle que nous voulons.Enfin, afin de s'assurer que le rectangle est usb, le programme calcule le coefficient de corrélation entre celui-ci et l'usb standard (la même méthode dans la correspondance de modèles ), et supprime ceux dont la similarité est trop faible.  
Cette méthode est très utile pour la détection d'objets sur la carte mère, elle peut détecter des segments de ligne à n'importe quel angle donné et peut contrôler l'épaisseur du segment de ligne. Dans le programme, la longueur du segment de ligne est donnée sous la forme d'un intervalle, et un segment de ligne (personnalisable) avec une longueur spécifiée de 0,9 à 1,1 fois est acceptable. Pour les graphiques comme les CPU et les processeurs à circuits intégrés, qui sont principalement rectangulaires et carrés, ils ont de bonnes performances. L'inconvénient est qu'il nécessite des arêtes vives et standard. Les crénelages, les cercles et les rectangles ont tous un effet désastreux sur l'algorithme.  

P.S. Dans le fonction de Huff transformation, il a besoins juste le longueur minimum. On donne longueur maximum par filtrer les résultats du Huff.

###  d-sub female et male
D-sub est une famille d'interfaces. Les plus courants sont vga et rs232. Ils se caractérisent par une disposition en quinconce de broches ou de trous. Les algorithmes de correspondance de modèles ne peuvent pas très bien distinguer les deux car leurs profils sont similaires. Deuxièmement, son contour n'est pas non plus rectangulaire. Un nouvel algorithme doit donc être envisagé.   
La détection des caractéristiques de l'image (certains matériaux sont appelés Corner Detection) peut obtenir le point d'angle de l'image, également appelé interest points, key points, feature points. Nous le comprenons simplement comme une classe d'algorithmes pour trouver des points où le gradient de l'image en niveaux de gris change rapidement, et il a une invariance de translation et de rotation. Il a de nombreuses méthodes, cette procédure est relativement nouvelle. Il détecte d'abord tous les points caractéristiques de l'image, dans ce cas, toutes les broches et tous les trous sont des points caractéristiques. Ensuite, parcourez chaque petit bloc pour calculer la similarité comme l'algorithme de correspondance de modèle, et trouvez le point maximum local. C'est juste que le programme n'utilise plus l'image d'origine, mais utilise l'image reconstruite des points caractéristiques. Générez des valeurs grises de densité de probabilité gaussienne autour de chaque point caractéristique. La reconstruction d'images surmonte les difficultés des différentes tailles de broches et des nuances de couleur dans différentes images. Il a une plus grande robustesse.  
Cette méthode peut être généralisée à tous les objets caractérisés par des épingles et des trous. Cette méthode peut également être essayée si un objet a une distribution unique de points caractéristiques. Pour la famille d-sub et l'interface PS/2, le même comportement est théoriquement disponible. Un modèle standard doit être sélectionné. De plus, la taille de la broche peut être contrôlée par min_scale et max_scale. L'inconvénient de cette méthode est que le concept de points caractéristiques est abstrait. Ce n'est pas très intuitif. Avant de courir, nous ne pouvons pas deviner quels points sont des points caractéristiques.  

### Slot, disque, Power unite
Ces pièces se présentent sous différentes formes et sont de grande taille. Il convient donc à le deep learning. Le deep learning ayant une forte capacité d’adaptation, il est souvent utilisé pour traiter des tâches complexes de détection de cibles. Dans le même temps, l'algorithme a été perfectionné. Il suffit simplement de le modifier.  
Pour tout algorithme de deep learning, les étapes de transformation sont les suivantes: étiqueter l'ensemble de données, configurer les hyperparamètres, entraîner le modèle et exporter le modèle d'entraînement. Lors de l'étape de prétraitement des données, le programme utilise des méthodes de rotation et d'épissage pour élargir l'ensemble de données et améliorer la capacité de généralisation de l'algorithme.
