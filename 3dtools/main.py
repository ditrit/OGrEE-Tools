from classifiers import Classifiers
import argparse
from pathlib import Path
from skimage.io import imsave
from os import remove
from ultralytics import YOLO
import numpy as np
from PIL import Image
from gui import run_gui


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
'''
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
'''
def run(servername ="image/serveur/dell-poweredge-r720xd.rear.png",
        height=87.38,
        width=443.99,
        face='face',
        model=ROOT / 'api/yolov8-best.pt',
        conf=0.25,
        iou=0.70,
        device='',
        augment=False,
        show=False,
        save=True,
        save_txt=False,
        save_conf=False,
        save_crop=False,
        show_label=True,
        show_conf=True,
        show_boxes=True,
        line_width=None,
        **kwargs
        ):
    #image = tools.impreprocess(image)
    ogreeTools = Classifiers(servername, height, width, face)
    model = YOLO(model)

    path = 'api/tmp' + servername.split('/')[-1]
    imsave(path, np.asarray(Image.open(servername).resize((640, 640))))
    # filter by class: --class 0, or --class 0 2 3
    class_dic = {'All': None, 'BMC': 0, 'Disk_lff': 1, 'Disk_sff': 2, 'Disks': [1, 2], 'PSU': 3, 'Serial': 4, 'Slot_lp': 5, 'Slot_normal': 6, 'Slots': [5, 6], 'USB': 7, 'VGA': 8}

    while True:
        print("\nChoose a component to detect.")
        print("Available commands: 'All', 'BMC', 'Disk_lff', 'Disk_sff', 'Disks', 'PSU', 'Serial', 'Slot_lp', 'Slot_normal', 'Slots', 'USB', 'VGA'.")
        print("Enter 'finish' to output the JSON.")
        print()
        command = input("Command: ")
        if command == "finish":
            break
        else:
            classes = class_dic.get(command, None)
            if classes is not None:
                print(f"Detecting {command}...")
                pred = model.predict(path, conf=conf, iou=iou, imgsz=640, half=False, device=device, max_det=400, visualize=False, 
                                          augment=augment, agnostic_nms=False, classes=classes, show=show, save=save, save_txt=save_txt, save_conf=save_conf, 
                                          save_crop=save_crop, show_labels=True, show_conf=show_conf, show_boxes=show_boxes, line_width=line_width)
                # pred: a list of tensor, each tensor represent a picture
                ogreeTools.dl_addComponents(pred)
            else:
                print("Invalid command. Try again.")
    ogreeTools.cutears()
    ogreeTools.writejson()
    ogreeTools.savejson()
    print(servername.split('/')[-1].split('.')[0], ' json file in "/api/"')
    remove(path)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', default=False, action='store_true', help='if provided, open GUI')
    parser.add_argument('--servername', type=str, default="image/serveur/dell-poweredge-r720xd.rear.png", help='model path or triton URL')
    parser.add_argument('--height', type=float, default=87.38, help="Server's height/vertical size" )
    parser.add_argument('--width', type=float, default=443.99, help="Server's width/horizon size")
    parser.add_argument('--face', default='rear', choices=['front', 'rear'], help='the picture is front bord or rear bord')
    #yolo hyparameters
    parser.add_argument('--model', nargs='+', type=str, default=ROOT/'api/yolov8-best.pt', help='model path or triton URL')
    parser.add_argument('--conf', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou', type=float, default=0.70, help='NMS IoU threshold')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--augment', default=False, action='store_true', help='if provided, augmented inference')
    parser.add_argument('--show', default=False, action='store_true', help='if provided, visualize features')
    parser.add_argument('--save', default=False, action='store_true', help='if provided, save detection results')
    parser.add_argument('--save-txt', action='store_true', help='if provided, save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='if provided, save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='if provided, save cropped prediction boxes')
    parser.add_argument('--show-labels', default=True, action='store_true', help='if provided, show labels')
    parser.add_argument('--show-conf', default=True, action='store_true', help='if provided, show confidences')
    parser.add_argument('--show-boxes', default=True, action='store_true', help='if provided, show bounding boxes')
    parser.add_argument('--line-width', default=None, type=int, help='bounding box line width (pixels)')
    opt = parser.parse_args()
    return opt


if __name__ == '__main__':
    opt = parse_opt()
    gui = vars(opt).pop('gui', False)

    if gui:
        run_gui(opt)
    else:
        run(**vars(opt))
