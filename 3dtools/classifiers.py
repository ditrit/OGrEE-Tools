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
        ACCURACY = 8

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
            for j in range(my):
                # Take a patch
                piece = self._image[i*ACCURACY:i*ACCURACY+105, j*ACCURACY:j*ACCURACY+290]
                feature_dark, feature_light = tools.imfeature(piece, self._mask, detector)
                # k-l divergence
                #matrix_vga[i,j] = tools.patchsimilarity(feature_dark,std_fvga)
                #matrix_rs232[i,j] = tools.patchsimilarity(feature_light,std_frs232)

                # gaussian describe
                matrix_vga[i, j] = tools.gaussiansimilarity(feature_dark, fvga_des)
                matrix_rs232[i, j] = tools.gaussiansimilarity(feature_light, frs232_des)

                print("finish ", i*ACCURACY, " ", j*ACCURACY, "  vga: ", matrix_vga[i, j])
        vga_list = ACCURACY*peak_local_max((matrix_vga-np.min(matrix_vga))/(np.max(matrix_vga)-np.min(matrix_vga))
                                           , threshold_abs=0.96, min_distance=3)
        rs232_list = ACCURACY*peak_local_max((matrix_rs232-np.min(
                matrix_rs232))/(np.max(matrix_rs232)-np.min(matrix_rs232)), threshold_rel=0.97)
        vga_list = [(i[1],i[0],0) for i in vga_list]
        rs232_list = [(i[1], i[0], 0) for i in rs232_list]
        tools.drawcomponents(self._image, vga_list, 290, 105)
        tools.drawcomponents(self._image, rs232_list, 290, 105)
        print("vga in :", vga_list)
        print("rs232 in :", rs232_list)

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
        position = tools.template_match(image_e, template_e, threshold, min_distance)
        print(position)
        for x, y, orin in position:
            self.components[(x, y)] = ("rj45", orin)


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
        #rectangles = tools.find_rectangle1(self._image, 120, 52, 2)  # usb: width =13.15mm, height = 5.70
        rectangles = tools.find_rectangle_(self._image, 120, 50, 2)  # usb: width =13.15mm, height = 5.70
        #for x, y, orin in rectangles:
        #    self.components[(x, y)] = ("usb", orin)
        print(rectangles)
        tools.drawcomponents(self._image, rectangles, 120, 52)
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


