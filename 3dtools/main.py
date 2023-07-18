import tools
from classifiers import Classifiers
import torch.multiprocessing
import argparse
from pathlib import Path
import api.yoloapi
from skimage.io import imsave

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
yROOT = ROOT / 'yolov5' # YOLOv5 root directory


'''
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
'''
def run(slotname ="serveur/dell-poweredge-r720xd.rear.png",
        height=86.8,
        length=482.4,
        weights=ROOT/'api/best.pt',  # model path or triton URL
        data=ROOT / 'yolov5/data/serveur72.yaml',  # dataset.yaml path
        imgsz=(192, 768),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=400,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        nosave=False,  # do not save images/videos
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'result/detect',  # save results to project/name
        name='sl_dis_pw',  # save results to project/name
        exist_ok=True,  # existing project/name ok, do not increment
        line_thickness=2,  # bounding box thickness (pixels)
        hide_labels=True,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        vid_stride=1,# video frame-rate stride
):
    #torch.multiprocessing.freeze_support()
    image = tools.imageload(slotname, "grey")
    #image = tools.impreprocess(image)
    ogreeTools = Classifiers(image, height, length)
    imsave('api/tmp.png', tools.scaleim(slotname, height, 2.0))
    # filter by class: --class 0, or --class 0 2 3
    class_dic = {'all': None, 'slot_normal': 0, 'slot_lp': 1, 'slot': [0, 1],
                 'disk_sff': 2, 'disk_lff': 3, 'disk': [2, 3], 'source': 4}
    while True:
        print("Enter componant name:")
        command = input()
        if command == "finish":
            break
        elif command == "vga&rs232":
            print("start detecting ", command)
            ogreeTools.clvga_rs232()
        elif command == "rj45":
            print("start detecting ", command)
            ogreeTools.clrj45()
        elif command == "usb":
            print("start detecting ", command)
            ogreeTools.clusb()
        elif command in class_dic.keys():
            print("start detecting ", command)
            pred = api.yoloapi.run(weights, 'api/tmp.png', data, imgsz, conf_thres, iou_thres, max_det, device, view_img,
                            save_txt, save_conf, save_crop, nosave, class_dic[command], agnostic_nms, augment, visualize, update,
                            project, name, exist_ok, line_thickness, hide_labels, hide_conf, half, dnn, vid_stride,)
            # pred: a list of tensor, each tensor represent a picture
            ogreeTools.addComponents(pred.cpu())

    ogreeTools.describe()


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--slotname', type=str, default="serveur/dell-poweredge-r720xd.rear.png", help='model path or triton URL')
    parser.add_argument('--height', type=float, default=86.8, help="Server's height/vertical size" )
    parser.add_argument('--length', type=float, default=482.4, help="Server's length/horizon size")
    #yolov5 hyparameter
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT/'api/best.pt', help='model path or triton URL')
    parser.add_argument('--conf-thres', type=float, default=0.5, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='if provided, show results')
    parser.add_argument('--save-txt', action='store_true', help='if provided, save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='if provided, save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='if provided, save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='if provided, do not save images/videos')
    parser.add_argument('--augment', action='store_true', help='if provided, augmented inference')
    parser.add_argument('--visualize', action='store_true', help='if provided, visualize features')
    parser.add_argument('--project', default=ROOT / 'detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='if provided, existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=1, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='if provided, hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='if provided, hide confidences')
    opt = parser.parse_args()

    return opt


def main(opt):
    run(**vars(opt))


if __name__ == '__main__':
    opt = parse_opt()
    main(opt)