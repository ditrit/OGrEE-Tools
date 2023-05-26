# 3d tools user guide

This is a user guide for 3d tools app, a powerful program which aide the 3d blender to generate the image of server with proper location of componants.   

# Explaination
## main.py
This is the general pilot of all the functions, and also the user interface.  
Some parameters should be told before start the program. 
> SLOTNAME : string  e.g SLOTNAME = "serveur/ibm-x3850x6.rear.png"
> HEIGHT : float  e.g. HEIGHT = 172.8
> LENGTH : float  e.g. LENGTH = 482.0
> other parameters in need, non-exhaustive list

after setting all the parameters for classifier(this step can also be replaced by executing data base automatically in the future), the program will creat a classifier class named ogree, then go on each defined classifier. Use ogree.clxxxx to detect component xxxx. It doesn't need any input at this step.

# Description of standard server (components): 
## standard image/components
We choose a model xxxxxxxx like the standard server. this image gives a ratio of 9.14x pixel /mm. and standard components rj45, rs232, vga are captured and are saved at the path /xxx/xxx.
explaination:
in std_vga, the ibm has draw  large holes in the picture. 


## Classifiers in Classifier class:
### clrj45:
Based on template matching, the program will use the standard image of rj45 to compare each slice of image, and calculate the similarity. Then a local_peak function is applied to find out the posible position where pass the threshould. (The threshould is setted as 0.x)

### clvgas232:
This classifier is designed to find vga or rs232 at the same time. Because they have the same shape. 
The methods applied is CENSURE algorithem. It process out the image features, which is pin positions here. 

### clsource: 
This classifier is designed to find power block in the image. We use the same template matching method to find out c14 interface. This gives a point situating in the block. Power block usually has a rectangle edge with a unit dimention. So we use a straight line detection function to find suspect rectangles of the same dimension. Last, an algorithem based on vector geometric calculation will decide whether the point is in this rectangle, i.e. is yhis the power bloc we are.searching.

#### Mark:
The unit dimention of power bloc differs among each producer. An data base is needed to be created to give this infoemation.q
