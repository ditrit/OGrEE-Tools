# COMPOS user guide

This is a user guide for COMPOS api, a powerful program who can locate the components on the board of server, output the coordinate in mm. After all, we can generate the model on the 2d face, then we put this face on the 3d model's front and back face.
## Components supported
| Name | method |
| ------ | ------ |
| rj45 | template matching |
| usb | rectangle detect |
| vga | image's feature points |
| rs232 | image's feature points |
| slot normal | YOLOV5 object detection |
| slot LP | YOLOV5 object detection |
| disk lff | YOLOV5 object detection |
| disk sff | YOLOV5 object detection |
| power supply unit | YOLOV5 object detection |
## Requirement
Infomation in [requirements.txt][PlDb]  
YOLOV5 needs to be cloned from [YOLOV5 official page](https://github.com/ultralytics/yolov5#tutorials) under root path.
## Introduction
### main.py
This is the general pilot of all the functions, and also the user interface.  
Here is a minimum tutorial example. 
```sh
cd Compos path
python main.py --slotname serveur/dell-poweredge-r720xd.rear.png --height 86.8 --length 482.4
```
Some basic parameters should be told before start the program. 
> --slotname : string, the file name of image. 
 --height : float, horizontal dimension, (unit mm).
 --length : float, vertical dimension, (unit mm).
>
User can also just run the *main.py* in python consoler. In this case, a default server "dell-poweredge-r720xd.rear.png" will be shown.

There are other parameters that the user can choose, to control algorithm's performance.  
> #yolov5 hyparameter
    --weights, type:str, model path or triton URL, if not want to change the yolov model, don't use it!
    --conf-thres, type:float, default=0.5, confidence threshold, yolov will filter the result less than it.
    --iou-thres, type=float, default=0.45, 'NMS IoU threshold'
    --device', default='cuda device, i.e. 0 or 0,1,2,3 or cpu'
    --view-img', if provided, show results on screen. 
    --save-txt', if provided, save results to *.txt'.
    --save-conf', if provided, save confidences in --save-txt labels'
    --save-crop', if provided, save cropped prediction boxes.
    --nosave', if provided, do not save images/videos'
    --augment', if provided, augmented inference'.
    --visualize', if provided, visualize features.
    --project', default=ROOT / 'detect', help='save results to project/name'
    --name', default='exp', Save results to "project/name"
    --exist-ok', If provided, existing project/name ok, do not increment, like exp1, exp2...
    --line-thickness', default=1, type=int, Bounding box thickness (pixels)
    --hide-labels', default=False, If provided, hide labels
    --hide-conf', default=False, action='store_true', help='if provided, hide confidences
>
After setting all the parameters for classifier(this step can also be replaced by executing data base automatically in the future), the program will creat a classifier class named ogree, then go on each defined classifier. Use ogree.clxxxx to detect component xxxx. It doesn't need any input at this step.

### Step
Use the following code to start the program.
```sh
cd COMPOS path
python main.py --slotname serveur/dell-poweredge-r720xd.rear.png --height 86.8 --length 482.4.
```


# Description of standard server (components): 
## standard image/components
We choose a model xxxxxxxx like the standard server. this image gives a ratio of 9.14x pixel /mm. and standard components rj45, rs232, vga are captured and are saved at the path /xxx/xxx.
explaination:
in std_vga, the ibm has draw  large holes in the picture. 


## Classifiers in *Classifier* class:
### clrj45:
Based on template matching, the program will use the standard image of rj45 to compare each slice of image, and calculate the similarity. Then a local_peak function is applied to find out the posible position where pass the threshould. (The threshould is setted as 0.x)

### clvgars232:
This classifier is designed to find vga or rs232 at the same time. Because they have the same shape. 
The methods applied is CENSURE algorithem. It process out the image features, which is pin positions here. 

### clusb: 
This classifier is designed to find power block in the image. We use the same template matching method to find out c14 interface. This gives a point situating in the block. Power block usually has a rectangle edge with a unit dimention. So we use a straight line detection function to find suspect rectangles of the same dimension. Last, an algorithem based on vector geometric calculation will decide whether the point is in this rectangle, i.e. is yhis the power bloc we are.searching.

#### Mark:
The unit dimention of power bloc differs among each producer. An data base is needed to be created to give this infoemation.q


