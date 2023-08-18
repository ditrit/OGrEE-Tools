import tools
from classifiers import Classifiers
import argparse
from pathlib import Path
import api.yoloapi
from skimage.io import imsave
from os import remove

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
yROOT = ROOT / 'yolov5'  # YOLOv5 root directory
'''
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
'''
def run(servername ="image/serveur/dell-poweredge-r720xd.rear.png",
        height=87.38,
        width=443.99,
        face='face',
        weights=ROOT/'api/best.pt',  # model path or triton URL
        data=ROOT / 'yolov5/data/serveur122.yaml',  # dataset.yaml path
        imgsz=(192, 768),  # inference size (height, width)
        conf_thres=0.60,  # confidence threshold
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
        vid_stride=1,  # video frame-rate stride
        ):
    #image = tools.impreprocess(image)
    ogreeTools = Classifiers(servername, height, width, face)

    path = 'api/tmp' + servername.split('/')[-1]
    imsave(path, tools.scaleim(servername, height, 2.0))
    # filter by class: --class 0, or --class 0 2 3
    class_dic = {'all': None, 'slot_normal': 0, 'slot_lp': 1, 'slot': [0, 1],
                 'disk_sff': 2, 'disk_lff': 3, 'disk': [2, 3], 'source': 4}
    while True:
        print('\nclass list: ', {'d-sub female': '11', 'd-sub male': '12', 'idrac': '13', 'usb': '14', 'all': '15'},
              "\nor enter the name 'slot', 'disk', 'source'(without '')",
              "\nPlease input one by one. Enter 'finish' to output the json")
        print("----Enter component name or code:")
        command = input()
        if command == "finish":
            break
        elif command == "d-sub female" or command == '11':
            print("start detecting d-sub female")
            ogreeTools.clvga_rs232('female')
        elif command == "d-sub male" or command == '12':
            print("start detecting d-sub male")
            ogreeTools.clvga_rs232('male')
        elif command == "idrac" or command == '13':
            print("start detecting idrac")
            ogreeTools.clidrac()
        elif command == "usb" or command == '14':
            print("start detecting usb")
            ogreeTools.clusb()
        elif command in class_dic.keys() or command == '15':
            print("start detecting slot&disk")
            command = 'all'
            pred = api.yoloapi.run(weights, path, data, imgsz, conf_thres, iou_thres, max_det, device, view_img,
                            save_txt, save_conf, save_crop, nosave, class_dic[command], agnostic_nms, augment, visualize, update,
                            project, name, exist_ok, line_thickness, hide_labels, hide_conf, half, dnn, vid_stride,)
            # pred: a list of tensor, each tensor represent a picture
            ogreeTools.dl_addComponents(pred.cpu())
    ogreeTools.cutears()
    ogreeTools.writejson()
    print(servername.split('/')[-1].split('.')[0], ' json file in "/api/"')
    remove(path)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--servername', type=str, default="image/serveur/dell-poweredge-r720xd.rear.png", help='model path or triton URL')
    parser.add_argument('--height', type=float, default=87.38, help="Server's height/vertical size" )
    parser.add_argument('--width', type=float, default=443.99, help="Server's width/horizon size")
    parser.add_argument('--face', default='rear', choices=['front', 'rear'], help='the picture is front bord or rear bord')
    #yolov5 hyparameter
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT/'api/best.pt', help='model path or triton URL')
    parser.add_argument('--conf-thres', type=float, default=0.60, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.50, help='NMS IoU threshold')
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