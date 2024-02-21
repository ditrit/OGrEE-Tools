# 3dtools user guide

This is a user guide for 'OGrEE-Tools/3dtools', a powerful program that can automatically locate components on an image of a server and output a JSON with their coordinates in mm. This output can be used to generate a bidimensional model of the face of the server. These bidimensional models of the back and front faces of a server can be combined to form a tridimensional model.

## Components supported

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

## Requirements

The minimum Python version required to use 3dtools is Python version 3.7.

YOLOV5 needs to be cloned from [YOLOV5 official page](https://github.com/ultralytics/yolov5#tutorials) in the `3dtools` directory.

Package infomation in [requirements.txt](requirements.txt)

## Setup

A setup script for 3dtools is provided under `/.../OGrEE-Tools/3dtools/setup.sh`. To use it, run:

```sh
git clone https://github.com/ditrit/OGrEE-Tools.git
cd OGrEE-Tools/3dtools
./setup.sh
```

## Introduction

### main.py
This is the general pilot of all the functions, and also the CLI.
Here is a minimum tutorial example.

```sh
cd /.../OGrEE-Tools/3dtools
python3 main.py --servername image/serveur/dell-poweredge-r720xd.rear.png --height 86.8 --length 482.4
```

Some basic parameters should be given as arguments.

> 
    --servername : string, the file name of image;
    --height : float, horizontal dimension (in mm);
    --length : float, vertical dimension (in mm);
    --face : string, 'front' or 'rear'.
>

You can also just run the *main.py* in python consoler. In this case, a default server "dell-poweredge-r720xd.rear.png" will be shown.

```sh
cd /.../OGrEE-Tools/3dtools
python3 main.py
```

Run `python3 main.py --gui` to interact with the Graphic User Interface (GUI).

![GUI](image/serveur/gui.png)

You can also set aditional parameters to control the algorithm's performance.

> 
    # YOLOV5 hyparameters
    --weights : string, model path or triton URL, if you don't want to change the YOLOV5 model, don't use it;
    --conf-thres : float, default=0.5, confidence threshold, YOLOV5 will filter the results below it;
    --iou-thres : float, default=0.45, 'NMS IoU threshold';
    --device : default=cuda device, i.e. 0 or 0,1,2,3 or cpu;
    --view-img : if provided, show results on screen;
    --save-txt : if provided, save results to *.txt;
    --save-conf : if provided, save confidences in --save-txt labels;
    --save-crop : if provided, save cropped prediction boxes;
    --nosave : if provided, won't save images';
    --augment : if provided, augmented inference;
    --visualize : if provided, visualize features;
    --project : default='ROOT/detect', save results to project/name;
    --name : default='exp', save results to 'project/name';
    --exist-ok : if provided, an existing project/name will be overwritten;
    --line-thickness : int, default=1, bounding box thickness (pixels);
    --hide-labels : default=False, if provided, hide labels;
    --hide-conf : default=False, if provided, hide confidences.
>

### Running the CLI

#### 1. Use the following code to start the program.

```sh
cd /.../OGrEE-Tools/3dtools
python3 main.py --servername image/serveur/dell-poweredge-r720xd.rear.png --height 86.8 --width 482.4 --face rear
```

#### 2. Select components for detection

The user will be prompted with the following message:

```sh
class list: {'d-sub female': '11', 'd-sub male': '12', 'idrac': '13', 'usb': '14', 'all': '15'} 
or enter the name 'slot', 'disk', 'source'(without '') 
Please input one by one. Enter 'finish' to output the json
----Enter component name or code:
```

Enter the wished name or code to start the detection.

Examples:

```sh
> d-sub female
> idrac
> 14
> 15
> slot
```
Results are printed, showing all detected components in the format `xxx in [x, y, angle, similarity]`.

```sh
start detecting d-sub female
0° searching progress:  100%:  ▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋

90° searching progress:  100%:  ▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋▋

vga in : [[640.0, 860.0, 0.0, 0.7698690075499673]]
```

**Attention:** the type of input code is *string*. If we want transform it into a interface connect with other program, the command should also be *string*, not int.

#### 3. Finish and output

After detecting all components, type in `finish` to start the output processing.

```sh
finish
```

The program will generate the JSON file and save it under folder `/.../OGrEE-Tools/3dtools/api` with the server name + '.json'. It will show:

```sh
{(16, 92): ('vga', 0.0, 0.8375591957768449), (16, 59): ('rs232', 0, 0.8667459425301842), ...}
dell-poweredge-r720xd  json file in "/api/"
```

The json file is written in the following format:

```json
[
    {
        "location": "vga0",
        "type": "vga",
        "elemOrient": "horizontal",
        "elemPos": [
            92.0,
            0,
            9.0
        ],
        "elemSize": [
            16.0,
            11.0,
            8.0
        ],
        "labelPos": "rear",
        "color": "",
        "attributes": {
            "factor": "",
            "similarity": 0.7698690075499673,
        }
    }
    ...
]
```

## Test example results

### JSON file

The JSON file of test example dell-poweredge-r720xd.rear should be similar to [test.json](api/test.json) if components 11, 12, 13, 14 and 15 are detected.

### 3d model

Original photo:

![Original photo](image/serveur/dell-poweredge-r720xd.rear.png)

3D model:

![3D model](image/serveur/test1.png)

![3D model](image/serveur/test2.png)

# Description of a standard server (components):

## Standard image/components

We chose model *ibm-x3690x5.rear.png* as the standard server. This image has a ratio of 9.14x pixel/mm. 

Standard idrac, rs232, vga and usb components were captured and saved at path `/.../OGrEE-Tools/3dtools/image/standard/`.

**Note:**: vga and rs232 components in IBM devices have slightly larger holes than other manufacturers.

Another idrac template was captured from model *cisco-c240-m6-lff.rear.png*, and is used for Cisco models.

**Note:** idrac components in Cisco devices have a different shape from other manufacturers (the pins are shorter).

## Classifiers in *Classifier* class:

### clidrac:

Based on template matching, the program will use the standard image of an idrac component to compare each slice of image, and calculate the similarity. Then, a local_peak function is applied to find out the best position to pass the threshold, set as 0.45.

### clvgars232:

This classifier is designed to find vga or rs232 at the same time, since they have the same shape. The method applied is the 'CENSURE algorithm', that processes out desired image features, which are pin positions in our case.

### clusb:

This classifier is designed to find usb components in the image. We use the same template matching method to find out where the components are, giving out possible points in the image. Usb components have a rectangle edge; a straight line detection function to find suspected rectangles of the same dimension in the image. Lastly, an vector geometric calculation will decide whether the points are in this rectangle, i.e. if the points belong to the usb components we are searching for.

### dl_addComponents:

This classifier is designed to find slots, disks and PSUs, and use the foreign YOLOV5 method for detection.

The `api` file of YOLOV5 is under `/.../OGrEE-Tools/3dtools/api/yoloapi.py`. It is similar to the one under `/.../OGrEE-Tools/3dtools/yolov5/detect.py`, but a bit simpler and with different coordinates treatment. Some unnecessary parameters and pieces of code have been moved. 

The user can detct all the slots, disks and PSUs with command `all` or with code `15`. These components can also be detected individually.

| Command | Components detected |
| ------ | ------ |
| all | slot normal, slot lp, disk sff, disk lff, psu |
| disk |  disk lff, disk sff |
| slot | slot normal, slot lp |
| disk_sff | disk sff |
| disk_lff | disk lff |
| slot_normal | slot normal |
| slot_lp | slot lp |
| source | power supply unit |

The detection results of YOLOV5 will be saved under `/.../OGrEE-Tools/3dtools/detect/exp x/`; the user can check the output there. Remember to clean the `detect` folder regularly, so it doesn't take up much memory.

#### Notes:

- The unit dimension of power supply units differ among manufacturers. A data base has to be created to account for this information;

- A spreadsheet with the shape of the server is stored under `/.../OGrEE-Tools/3dtools/image/name_list.xlsx`. Use with caution, as some data might be incorrect;

- A very common error is to inverse the x and y axis, because the indexes in different libraries are not the same; some use (vertical, horizontal), while others use (horizontal, vertical). For the further programming, check the axis order when the classifier finds a component at the wrong position but with high similarity, or when the component position is out of the picture. The user can trust that the present version works properly.

- In 3dtools code, the origin point is situated on the top left corner of the picture; in the JSON file, the 3D origin point is situated on the back bottom right corner of the model.
