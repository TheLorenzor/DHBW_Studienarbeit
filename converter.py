import os
from classes import BoschFilter, DTLD

if __name__ =="__main__":

    all_imgs = os.listdir(os.path.join("datasets", "trafficlights", "train", "images"))
    if all_imgs == 0:
        bosch = BoschFilter("D:\Programmieren\\Uni\Studienarbeit\datasets\Rohdaten\Bosch Training Dataset","D:\Programmieren\\Uni\Studienarbeit\datasets\\trafficlights\\train")
        bosch.convertToJPGLarge()
        bosch.convertToJPGSmall()
        print("Bosch finished")

    daimler = DTLD()
    daimler.read_all_JSON()
