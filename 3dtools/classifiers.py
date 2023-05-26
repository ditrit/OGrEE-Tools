'''
Before use these classifiers, please make sure following things:
Herein, all the patch/template are in the same scale pixel/mm.
VGA and RS232 templates are taken from dell-poweredge-r740xd.rear  (x,y,z)
and regulizied in 105*290(height*long)
'''



import tools
import numpy as np
from skimage.feature import CENSURE,peak_local_max


class Classifiers:
    def clvga_rs232(self):
        ACCURACY = 20
        detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)

        std_fvga,_ = tools.imfeature(self._vga*self._mask,detector)
        _,std_frs232 = tools.imfeature(self._rs232*self._mask,detector)
        mx = (self._image.shape[0]-104)//ACCURACY
        my = (self._image.shape[1]-289)//ACCURACY
        matrix_vga = np.zeros([mx,my])
        matrix_rs232 = np.zeros([(self._image.shape[0]-104)//ACCURACY,(self._image.shape[1]-289)//ACCURACY])

        fvga_des = [tools.Pin(x,y) for x,y in std_fvga]
        frs232_des = [tools.Pin(x,y) for x,y in std_frs232]

        for i in range(mx):
            for j in range(my):
                # Take a patch
                piece = self._image[i*ACCURACY:i*ACCURACY+105,j*ACCURACY:j*ACCURACY+290]
                feature_dark, feature_light = tools.imfeature(piece*self._mask,detector)
                # delete features in mask
                idx = []
                for k in range(feature_dark.shape[0]):
                    if not self._mask[feature_dark[k, 0], feature_dark[k, 1]]:
                        idx.append(k)
                feature_dark = np.delete(feature_dark, idx, 0)
                idx = []
                for k in range(feature_light.shape[0]):
                    if not self._mask[feature_light[k, 0], feature_light[k, 1]]:
                        idx.append(k)
                feature_light = np.delete(feature_light, idx, 0)
                # k-l divergence
                #matrix_vga[i,j] = tools.patchsimilarity(feature_dark,std_fvga)
                #matrix_rs232[i,j] = tools.patchsimilarity(feature_light,std_frs232)

                # gaussian describe
                matrix_vga[i,j] = tools.gaussiansimilarity(feature_dark,fvga_des)
                matrix_rs232[i,j] = tools.gaussiansimilarity(feature_light,frs232_des)

                print("finish ", i*ACCURACY," ",j*ACCURACY,"  vga: ",matrix_vga[i,j] )


        vga_list = peak_local_max((matrix_vga-np.min(matrix_vga))/(np.max(matrix_vga)-np.min(matrix_vga)), threshold_abs=0.98)
        rs232_list = peak_local_max((matrix_rs232-np.min(matrix_rs232))/(np.max(matrix_rs232)-np.min(matrix_rs232)), threshold_rel=0.98)
        print("vga in :", vga_list)
        print("rs232 in :", rs232_list)

    def test(self):
        import scipy.stats
        detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
        std_fvga,_ = tools.imfeature(self._vga*self._mask,detector)
        _,std_frs232 = tools.imfeature(self._rs232*self._mask,detector)
        KL = tools.klentropy(std_fvga,std_frs232)
        print(KL)

    def clrj45(self):
        min_distance = 60
        threshold = 0.60
        template_e = tools.imedge(self._rj45)
        tools.templateMatch(self._image, template_e,threshold,min_distance)

    def clsource(self):

        #clc14
        min_distance = 40
        threshold = 0.55
        template_e = tools.imedge(self._c14)
        points = tools.templateMatch(self._image, template_e,threshold,min_distance)
        #detect rectangle based on edge
        rectangles = tools.findRectangle(self._image,650, 338)
        for i in points:
            for j in rectangles:
                if tools.inRectangle(i,j):
                    print("source position is :  ",j)

    def textjson(self):
        for i in self.components:
            pass


    
    def __init__(self,image,x,y):
        self._image = tools.normaliseimage(image,x,y)
        self._mask = tools.imageload('/standard/mask.png','grey')
        self._vga = tools.imageload('/standard/standard-vga.png','grey')
        self._rs232 = tools.imageload('/standard/standard-rs232.png','grey')
        self._rj45 = tools.imageload('/standard/standard-rj45.png','grey')
        self._c14 = tools.imageload('/standard/standard-c14.png','grey')
        self.components = dict()


