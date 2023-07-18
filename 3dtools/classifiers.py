"""
Before use these classifiers, please make sure following things:
Herein, all the patch/template are in the same scale pixel/mm.
VGA and RS232 templates are taken from ibm-x3690x5.rear  (x,y,z)
and regulizied in 105*290(height*long)
"""


import tools
#import parallelmethode
import numpy as np
from skimage.feature import CENSURE,peak_local_max
import sys

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

        detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
        std_fvga, _ = tools.imfeature(self._vga, self._mask, detector)
        _, std_frs232 = tools.imfeature(self._rs232, self._mask, detector)
        mx = (self._image.shape[0]-104)//ACCURACY
        my = (self._image.shape[1]-289)//ACCURACY
        fvga_des = tools.Pins(std_fvga)
        frs232_des = tools.Pins(std_frs232)

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
        print('\n')
        vga_list = peak_local_max((matrix_vga-np.min(matrix_vga))/(np.max(matrix_vga)-np.min(matrix_vga))
                                           , threshold_abs=0.97, min_distance=1)
        rs232_list = peak_local_max((matrix_rs232-np.min(matrix_rs232))/(np.max(matrix_rs232)-np.min(matrix_rs232))
                                             , threshold_rel=0.97, min_distance=1)
        vga_list = [(h*ACCURACY, w*ACCURACY, 0, matrix_vga[h, w]) for h, w in vga_list]
        rs232_list = [(h*ACCURACY, w*ACCURACY, 0, matrix_rs232[h, w]) for h, w in rs232_list]
        tools.drawcomponents(self._image, vga_list, 290, 105)
        tools.drawcomponents(self._image, rs232_list, 290, 105)
        print("vga in :", vga_list)
        print("rs232 in :", rs232_list)
        for x, y, ang, sim in vga_list:
            self.components[(x, y)] = ("vga", ang, sim)
        for x, y, ang, sim in rs232_list:
            self.components[(x, y)] = ("rs232", ang, sim)

    def clvga_rs232gpu(self):
        import torch
        import torch.multiprocessing as mp

        def parallel_calculation(matrix, batch_size):
            num_rows, num_cols = mx, my
            g_function = parallelmethode.parapara(detector,mask,fvga_des)

            # Create a shared memory tensor to store the results
            result_matrix = torch.zeros([num_rows, num_cols])

            # Generate indices for parallel processing
            indices = []
            for i in range(num_rows):
                for j in range(num_cols):
                    indices.append((i, j))

            # Create a pool of processes to perform the calculations in parallel
            with mp.Pool(10) as pool:
                # Split the indices into batches
                batches = [indices[i:i + batch_size] for i in range(0, len(indices), batch_size)]

                # Process each batch in parallel using map
                results = pool.map(g_function.imfeature, matrix)#############################3

                # Update the result_matrix using the calculated values
                for idx, (row_idx, col_idx) in enumerate(
                        [(row_idx, col_idx) for batch in batches for row_idx, col_idx in batch]):
                    result_matrix[row_idx, col_idx] = results[idx]

            return result_matrix

        # Example usage

        # Set the batch size for parallel processing
        batch_size = 4
        ACCURACY = 20
        mx = (self._image.shape[0] - 104) // ACCURACY
        my = (self._image.shape[1] - 289) // ACCURACY

        # Create a matrix
        matrix = parallelmethode.creatdata(mx,my,ACCURACY,self._image)
        matrix = torch.tensor(matrix)

        detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
        std_fvga, _ = tools.imfeature(self._vga, self._mask, detector)
        _, std_frs232 = tools.imfeature(self._rs232, self._mask, detector)
        fvga_des = [tools.Pin(x, y) for x, y in std_fvga]       # distribution of pins
        frs232_des = [tools.Pin(x, y) for x, y in std_frs232]   # distribution of pins
        mask = torch.tensor(self._mask)
        # Perform parallel calculation
        result = parallel_calculation(matrix, batch_size)

        print("Result Matrix:")
        print(result)



    def test(self):
        detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
        std_fvga, _ = tools.imfeature(self._vga*self._mask, detector)   ######## ?
        _, std_frs232 = tools.imfeature(self._rs232*self._mask, detector)
        KL = tools.klentropy(std_fvga, std_frs232)
        print(KL)

    def clrj45(self):
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
        min_distance = 40
        threshold = 0.50

        template_e = tools.imedge(self._rj45)
        image_e = tools.imedge(self._image)
        position_sim = tools.template_match(image_e, template_e, threshold, min_distance)
        print(position_sim)
        for x, y, ang, sim in position_sim:
            self.components[(x, y)] = ("rj45", ang, sim)



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
        rectangles = tools.find_rectangle1(self._image, 120, 50, 2)  # usb: width =13.15mm, height = 5.70
        if rectangles:
            for i in range(len(rectangles)):
                x, y = rectangles[i]
                sim = tools.modsimilarity(self._image[x:x+120, y:y+50], self._usb)
                rectangles[i] = (x, y, 90, sim)
                self.components[(x, y)] = ('usb', 90, sim)
            tools.drawcomponents(self._image, rectangles, 120, 50)
        rectangles = tools.find_rectangle_(self._image, 120, 50, 2)  # usb: width =13.15mm, height = 5.70
        if rectangles:
            for i in range(len(rectangles)):
                x, y = rectangles[i]
                sim = tools.modsimilarity(self._image[x:x+120, y:y+50], self._usb)
                rectangles[i] = (x, y, 0, sim)
                self.components[(x, y)] = ('usb', 0, sim)
            tools.drawcomponents(self._image, rectangles, 120, 50)
        #for x, y, orin in rectangles:
        #    self.components[(x, y)] = ("usb", orin)


        '''
        min_distance = 40
        threshold = 0.45

        template_e = tools.imedge(self._usb)
        image_e = tools.imedge(self._image)
        position = tools.template_match(image_e, template_e, threshold, min_distance)
        for x, y, orin in position:
            self.components[(x, y)] = ("usb", orin)
        '''


    def clsource(self):
        """
        Find the power supply in the image.

        Args:
            non

        Constance:
            min_distance: parameter of peaklocalmax
            threshold: parameter of peaklocalmax

        Returns:
            Coordinates of rj45 in the picture.
        """
        # clc14
        min_distance = 40
        threshold = 0.50

        template_e = tools.imedge(self._c14)
        image_e = tools.imedge(self._image)
        points = [p[:2] for p in tools.template_match(image_e, template_e, threshold, min_distance)]
        # detect rectangle based on edge
        rectangles = tools.find_rectangle(self._image, 737, 365, 7)   # source: width, height
        for i in points:
            for j in rectangles:
                if tools.in_rectangle(i, j):
                    print("source position is :  ", j)

    def addComponents(self, pred, name=0, angle=0):
        """
        Add components by other method, such as yolov. It can also be a coordinate marked by hand.

        Args:
            compos: a tensor or nd.array of components
        """
        # pred: [class, sim,x,y,x,y]
        class_dic = {0: 'slot_normal', 1: 'slot_lp', 2: 'disk_sff', 3: 'disk_lff', 4: 'source'}

        for i in pred:
            if name == 0:
                name = class_dic[int(i[0])]
            self.components[tuple(np.floor(i[4:6].numpy()*self._image.shape))] = (name, angle, i[1])

    def describe(self):
        """
        Generate JSON text of components in dict self.components

        Args:
            non

        Returns:
            JSON text
        """
        slots = []
        self.components = tools.calibrateear(self.components, self._image.shape, self._shapemm)  # cut the ear if exist
        for pos in self.components:
            path = "templates/components/"+self.components[pos][0]+".json"
            slots.append(tools.jsonwrite(pos, path))
        print(slots)

    def __init__(self, image, x, y):
        self._shapemm = (x, y)
        self._image = tools.normaliseimage(image, self._shapemm)
        self._mask = tools.imageload('/standard/mask.png', 'grey')
        self._vga = tools.imageload('/standard/standard-vga.png', 'grey')
        self._rs232 = tools.imageload('/standard/standard-rs232.png', 'grey')
        self._rj45 = tools.imageload('/standard/standard-rj45.png', 'grey')
        self._usb = tools.imageload('/standard/standard-usb.png', 'grey')
        self._c14 = tools.imageload('/standard/standard-c14.png', 'grey')
        self.components = dict()
        tools.rgbview(self._image)