"""
Before use these classifiers, please make sure following things:
Herein, all the patch/template are in the same scale pixel/mm.
VGA and RS232 templates are taken from ibm-x3690x5.rear  (x,y,z)
and regulizied in 95*180(height*long)
"""
import tools
import numpy as np
from skimage.feature import CENSURE
from tkinter import *
import json


class Classifiers:
    def dl_addComponents(self, pred):
        """
        Add components detected by YOLOv8 model.
        """

        class_dic = {0: 'RJ45', 1: 'Disk_lff', 2: 'Disk_sff', 3: 'PSU', 4: 'Serial', 5: 'Slot_lp', 6: 'Slot_normal', 7: 'USB', 8: 'VGA'}

        boxes = pred[0].boxes.numpy()
        
        for component in boxes:
            compotype = class_dic[component.cls[0]]
            x, y, _, _ = component.xyxy[0]
            _, _, w, h = component.xywh[0]
            position = (int(y * tools.RATIO * self._shapemm[0] / 640), int(x * tools.RATIO * self._shapemm[1] / 640))
            dimensions = (int(h * tools.RATIO * self._shapemm[0] / 640), int(w * tools.RATIO * self._shapemm[1] / 640))
            angle = 0
            if h * tools.RATIO * self._shapemm[0] / 640 > w * tools.RATIO * self._shapemm[1] / 640:
                angle = 90
            sim = component.conf[0]
            
            self.components[position] = (compotype, compotype, "components", angle, sim, dimensions)
            print(f"  - {compotype} in : " + str([position, angle, sim]))

        if len(boxes) == 0:
            print("  - Nothing found")

    def cutears(self):
        """
        Determine if there is a pair of ears in the image.
        If so, the components' position will be recalculated if they are posed in a non-ear server.

        Returns:
            JSON text with the coordinates without ears.
        """
        ear = 0.5 * (self._image.shape[1] - self._image.shape[0] * self._shapemm[1] / self._shapemm[0])
        self.componentsmm = dict()
        if ear < 0:
            for i in self.components:
                value = self.components[i]
                if self._face == 'front':
                    key = (int((self._image.shape[0] - i[0]) / tools.RATIO), int((self._image.shape[1] - i[1]) / tools.RATIO))
                else:
                    key = (int((self._image.shape[0] - i[0]) / tools.RATIO), int(i[1] / tools.RATIO))
                self.componentsmm[key] = value
        else:
            for i in self.components:
                value = self.components[i]
                if self._face == 'front':
                    key = (int((self._image.shape[0] - i[0]) / tools.RATIO), int((self._image.shape[1] - i[1] - ear) / tools.RATIO))
                else:
                    key = (int((self._image.shape[0] - i[0]) / tools.RATIO), int((i[1] - ear) / tools.RATIO))
                self.componentsmm[key] = value
        # print(self.componentsmm)

    def writejson(self):
        """
        Generate JSON text of components in dict self.components
        :return: 'servername.json' stocked in file api
        """
        jsonraw = {"components":[], "slots":[]}
        num = 0
        if self._face == 'rear':
            for k in self.componentsmm:
                name, compotype, compocategory, angle, similarity, _ = self.componentsmm[k]
                composhape = self.sizetable[compotype] if angle == 0 else self.sizetable[compotype][::-1]
                jsonraw[compocategory].append({"location": name+str(num), "type": compotype, "elemOrient": 'horizontal' if angle == 0 else 'vertical',
                                'elemPos': [round(float(k[1]), 1), 0, round(float(k[0] - composhape[2]), 1)],
                                "elemSize": composhape, "labelPos": 'rear',
                                "color": "", "attributes": {"factor": "", 'similarity': str(similarity)}})
                num += 1
        else:
            for k in self.componentsmm:
                name, compotype, compocategory, angle, similarity, _ = self.componentsmm[k]
                composhape = self.sizetable[compotype] if angle == 0 else self.sizetable[compotype][::-1]
                jsonraw[compocategory].append({"location": str(num) + name, "type": compotype, "elemOrient": 'horizontal' if angle == 0 else 'vertical',
                                'elemPos': [round(float(k[1]) - composhape[0], 1), round(756.67 - composhape[1], 1), round(float(k[0] - composhape[2]), 1)],
                                "elemSize": composhape, "labelPos": 'front',
                                "color": "", "attributes": {"factor": "", 'similarity': str(similarity)}})
                num += 1
        self.jsonraw = jsonraw
        self.formatjson = json.dumps(jsonraw, indent=4)
        return self.formatjson

    def savejson(self):
        # Step 1: Define the file path where you want to save the JSON data
        file_path = 'api/'+self._name+'_'+self._face+'.json'
        # Step 2: Write the dictionary to the JSON file
        tools.jsondump(file_path, self.jsonraw)
        print(self.formatjson)

    def getjson(self):
        return self.formatjson

    def __init__(self, servername, x, y, face):
        self._shapemm = (x, y)
        self._name = servername.split('/')[-1].split('.')[0]
        self._face = face
        self._image = tools.normaliseimage(tools.imageload(servername, "grey"), self._shapemm)
        self._mask = tools.imageload('image/standard/mask.png', 'grey')
        self._vga = tools.imageload('image/standard/standard-vga.png', 'grey')
        self._rs232 = tools.imageload('image/standard/standard-rs232.png', 'grey')
        self._idrac = tools.imageload('image/standard/standard-idrac.png', 'grey')
        self._idrac_cisco = tools.imageload('image/standard/cisco-idrac.png', 'grey')
        self._usb = tools.imageload('image/standard/standard-usb.png', 'grey')
        self.sizetable = tools.SIZETABLE
        self.components = dict()
        self.componentsmm = dict()
        # tools.rgbview(self._image)
