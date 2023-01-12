import os
import cv2
import numpy as np
from PIL import Image
from classes import BoschFilter
from matplotlib import cm
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt



baseDirecotry = "./datasets/Rohdaten/"



def DTLDNormalize():
    # reads path
    imgPath = "D:\Programmieren\\Uni\Studienarbeit\datasets\Rohdaten\DTLD\Pictures\Berlin\Berlin\Berlin1\\2015-04-17_10-50-05\DE_BBBR667_2015-04-17_10-50-13-633939_k0.tiff"
    # reads it as unchanged thread of data
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    # converts it via the  bayer filter into an rgb image
    img = cv2.cvtColor(img, cv2.COLOR_BAYER_GB2BGR)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img = np.right_shift(img, 4)
    # set the right tones (convert to 8bit from 12 bit)
    img = img.astype(np.uint8)
    im = Image.fromarray(img)
    # save as jpgf
    im.save("test.jpg", quality=95)

#DTLDNormalize()


bosch = BoschFilter("D:\Programmieren\\Uni\Studienarbeit\datasets\Rohdaten\Bosch Training Dataset","D:\Programmieren\\Uni\Studienarbeit\datasets\\trafficlights\\train")
bosch.convertToJPGLarge()
bosch.convertToJPGSmall()
