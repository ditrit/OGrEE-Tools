"""
Before use these classifiers, please make sure following things:
Herein, all the patch/template are in the same scale pixel/mm.
VGA and RS232 templates are taken from ibm-x3690x5.rear  (x,y,z)
and regulizied in 105*290(height*long)
"""
import tools
import numpy as np
from skimage.feature import CENSURE, peak_local_max


class Classifiers:
    def clvga_rs232(self):
        """
        Find the vga and rs232 in the image.

        Args:

        Constance:
            ACCURACY: step of moving in pixels. Minimum is 1

        Returns:
            Coordinates of vga and rs232 in the picture.
        """
        ACCURACY = 20
        vga_list = []
        rs232_list = []
        detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
        std_fvga, _ = tools.imfeature(self._vga, self._mask, detector)
        _, std_frs232 = tools.imfeature(self._rs232, self._mask, detector)
        fvga_des = tools.Pins(std_fvga,'vga').destribution()
        frs232_des = tools.Pins(std_frs232,'rs232').destribution()
        im_dark, _ = tools.imfeature(self._image, np.ones_like(self._image), detector)
        _, im_bright = tools.imfeature(self._image, np.ones_like(self._image), detector)
        imdark_des = tools.Pins(im_dark,'vga',np.array(self._image.shape)).destribution()
        imbright_des = tools.Pins(im_bright,'rs232',np.array(self._image.shape)).destribution()
        '''
        matrix_vga = np.zeros([(self._image.shape[0]-104)//ACCURACY, (self._image.shape[1]-289)//ACCURACY])
        matrix_rs232 = np.zeros([(self._image.shape[0]-104)//ACCURACY, (self._image.shape[1]-289)//ACCURACY])
        
        for i in range(mx):
            print("\r", end="")
            print("Searching progress: {}%: ".format(int(i/mx*100)), "▋" * int(i * 50 /mx), end="")
            sys.stdout.flush()
            for j in range(my):
                # Take a patch
                piece = self._image[i*ACCURACY:i*ACCURACY+105, j*ACCURACY:j*ACCURACY+290]
                feature_dark, feature_light = tools.imfeature(piece, self._mask, detector)
                pin_dark = tools.Pins(feature_dark)
                pin_light = tools.Pins(feature_light)
                # gaussian describe
                matrix_vga[i, j] = tools.modsimilarity(pin_dark.destribution(), fvga_des.destribution())
                matrix_rs232[i, j] = tools.modsimilarity(pin_light.destribution(), frs232_des.destribution())
                #print("finish ", i*ACCURACY, " ", j*ACCURACY, "  vga: ", matrix_vga[i, j])
        '''

            # print("finish ", i*ACCURACY, " ", j*ACCURACY, "  vga: ", matrix_vga[i, j])
        tmpvga, tmprs232 = tools.paramatch(ACCURACY, imdark_des, imbright_des, 0, fvga_des, frs232_des, self._mask)
        vga_list += tmpvga
        rs232_list += tmprs232

        tmpvga, tmprs232 = tools.paramatch(ACCURACY, imdark_des, imbright_des, 90,
                                           np.rot90(fvga_des, -1), np.rot90(frs232_des, -1), np.rot90(self._mask, -1))
        vga_list += tmpvga
        rs232_list += tmprs232

        vga_list = tools.composantfilter(vga_list, 180+95)
        rs232_list = tools.composantfilter(rs232_list, 180+95)
        #tools.drawcomponents(self._image, vga_list, 180, 95)
        #tools.drawcomponents(self._image, rs232_list, 180, 95)
        print("vga in :", vga_list)
        print("rs232 in :", rs232_list)
        for x, y, ang, sim in vga_list:
            self.components[(x, y)] = ("vga", ang, sim)
        for x, y, ang, sim in rs232_list:
            self.components[(x, y)] = ("rs232", ang, sim)

    def clidrac(self):
        """
        Find the rj45 in the image.

        Args:
            non

        Constance:
            min_distance: parameter of peaklocalmax
            threshold: parameter of peaklocalmax

        Returns:
            Coordinates of rj45 in the picture.
        """
        min_distance = 35
        threshold = 0.45
        template_e = tools.imedge(self._idrac)
        image_e = tools.imedge(self._image)
        position_sim1 = tools.template_match(image_e, template_e, threshold, min_distance)
        template_e = tools.imedge(self._idrac_c)
        position_sim2 = tools.template_match(image_e, template_e, threshold, min_distance)
        #position_sim = tools.composantfilter(position_sim, 116+89)
        position_sim = position_sim1 if len(position_sim1)>len(position_sim2) else position_sim2
        print(position_sim)

        for x, y, ang, sim in position_sim:
            self.components[(x, y)] = ("idrac", ang, sim)



    def clusb(self):
        """
        Find the usb in the image.

        Args:
            non

        Constance:
            min_distance: parameter of peaklocalmax
            threshold: parameter of peaklocalmax

        Returns:
            Coordinates of rj45 in the picture.
        """
        def produce_rect(args):
            x, y = args[1], args[0]
            if angle == 0:
                sim = tools.modsimilarity(tools.imedge(self._image[x-1:x + 48-1, y-2:y + 122-2]), stdedge)
            elif angle == 90:
                sim = tools.modsimilarity(self._image[x-2:x + 122-2, y-1:y + 48-1], stdedge.T)
            return [x, y, angle, sim]
        stdedge = tools.imedge(self._usb)
        rectangles = tools.find_rectangle1(self._image, 122, 48, 2)  # usb: width =13.15mm, height = 5.70
        if rectangles:
            angle = 90
            usbs = list(map(produce_rect, rectangles))
            usbs = tools.composantfilter(usbs, 48+122)
            for c in usbs:
                print("usb in:  ", c)
                self.components[(c[0], c[1])] = ('usb', angle, c[3])
            #tools.drawcomponents(self._image, rectangles, 120, 50)
        rectangles = tools.find_rectangle_(self._image, 122, 48, 2)  # usb: width =13.15mm, height = 5.70
        if rectangles:
            angle = 0
            usbs = list(map(produce_rect, rectangles))
            usbs = tools.composantfilter(usbs, 48+122)
            for c in usbs:
                print("usb in:  ", c)
                self.components[(c[0], c[1])] = ('usb', angle, c[3])
            #tools.drawcomponents(self._image, rectangles, 120, 50)



    def norm_addComponents(self, pred, name=0, angle=0):
        """
        Add components by normal mathematic method, such as yolov. It can also be a coordinate marked by hand.

        Args:
            compos: a tensor or nd.array of components
        """
        # pred: [class, sim,x,y,x,y]

        class_dic = {0: 'slot_normal', 1: 'slot_lp', 2: 'disk_lff', 3: 'disk_sff', 4: 'source'}
        if name == 0:
            for i in pred:
                angle = 0
                name = class_dic[int(i[0])]
                if (i[2]-i[4])*self._image.shape[0] > (i[3]-i[5])*self._image.shape[1]:
                    angle = 90
                self.components[tuple(np.floor(i[4:6].numpy()*self._image.shape))] = (name, angle, float(i[1]))



    def dl_addComponents(self, pred, name=0, angle=0):
        """
        Add components by other method, such as yolov. It can also be a coordinate marked by hand.

        Args:
            compos: a tensor or nd.array of components
        """
        # pred: [class, sim,x,y,x,y]

        class_dic = {0: 'slot_normal', 1: 'slot_lp', 2: 'disk_lff', 3: 'disk_sff', 4: 'PSU'}
        if name == 0:
            for i in pred:
                angle = 0
                name = class_dic[int(i[0])]
                if (i[2]-i[4])*self._image.shape[0] > (i[3]-i[5])*self._image.shape[1]:
                    angle = 90
                    self.sizetable[name][2] = round(float(i[3]-i[5])*self._image.shape[1]/tools.RATIO, 1)
                else:
                    self.sizetable[name][2] = round(float(i[2]-i[4])*self._image.shape[0]/tools.RATIO, 1)
                self.components[tuple(np.floor(i[4:6].numpy()*self._image.shape))] = (name, angle, float(i[1]))
                print("%s in:  "%name, [tuple(np.floor(i[4:6].numpy()*self._image.shape)), angle, float(i[1])])


    def describe(self):
        """=
        Generate JSON text of components in dict self.components
        Determing is there a pair of ears in the image.
        If so, the components' position will be recalculated if they are posed in a non-ear server.

        Args:
            non

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
        print(self.componentsmm)

    def writejson(self):
        jsonraw = []
        num = 0
        if self._face == 'rear':
            for k in self.componentsmm:
                name, angle, similarity = self.componentsmm[k]
                composhape = self.sizetable[name] if angle == 0 else [self.sizetable[name][2], self.sizetable[name][1], self.sizetable[name][0]]
                jsonraw.append({"location": name+str(num), "type": "", "elemOrient": 'horizontal',
                                'elemPos': [float(k[1]), 0, float(k[0] - composhape[2])],
                                "elemSize": composhape, "labelPos": 'rear',
                                "color": "", "attributes": {"factor": "", 'similarity': similarity}})
                num += 1
        else:
            for k in self.componentsmm:
                name, angle, similarity = self.componentsmm[k]
                composhape = self.sizetable[name] if angle == 0 else [self.sizetable[name][2], self.sizetable[name][1], self.sizetable[name][0]]
                jsonraw.append({"location": str(num) + name, "type": "", "elemOrient": 'horizontal',
                                'elemPos': [float(k[1]) - composhape[0], 756.67 - composhape[1], float(k[0] - composhape[2])],
                                "elemSize": composhape, "labelPos": 'front',
                                "color": "", "attributes": {"factor": "", 'similarity': similarity}})
                num += 1
        # Step 1: Define the file path where you want to save the JSON data
        file_path = 'api/'+self._name+'_'+self._face+'.json'
        # Step 2: Write the dictionary to the JSON file
        tools.jsondump(file_path, jsonraw)

    def __init__(self, slotname, x, y, face):
        self._shapemm = (x, y)
        self._name = slotname.split('/')[-1]
        self._face = face
        self._image = tools.normaliseimage(tools.imageload(slotname, "grey"), self._shapemm)
        self._mask = tools.imageload('/standard/mask.png', 'grey')
        self._vga = tools.imageload('/standard/standard-vga.png', 'grey')
        self._rs232 = tools.imageload('/standard/standard-rs232.png', 'grey')
        self._idrac = tools.imageload('/standard/standard-idrac.png', 'grey')
        self._idrac_c = tools.imageload('/standard/cisco-idrac.png', 'grey')
        self._usb = tools.imageload('/standard/standard-usb.png', 'grey')
        self.sizetable = tools.SIZETABLE
        self.components = dict()
        self.componentsmm = dict()
        tools.rgbview(self._image)