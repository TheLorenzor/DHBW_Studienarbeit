import os
from PIL import Image
import yaml





class BoschFilter():
    def __init__(self,basePath,dest):
        self.dataSetSmall_path = os.path.join(os.path.realpath(basePath), "dataset_additional_rgb")
        self.datasetLarge_path = os.path.join(os.path.realpath(basePath), "train_rgb")
        # convert the yaml to lists for reading the boxes later
        self.datasetLargeDescr = yaml.safe_load(open(os.path.join(self.datasetLarge_path, "train.yaml")))
        self.datasetSmallDescr = yaml.safe_load(open(os.path.join(self.dataSetSmall_path, "additional_train.yaml")))
        # get to the data check
        self.dataSetSmall_path = os.path.join(self.dataSetSmall_path, "rgb", "additional")
        self.datasetLarge_path = os.path.join(self.datasetLarge_path, "rgb", "train")

        self.destPath = dest
    def convertToJPGLarge(self):

        dirs = os.listdir(self.datasetLarge_path)
        for singleDir in dirs:
            newPath =os.path.join(self.datasetLarge_path,singleDir)
            pictureNames = os.listdir(newPath)
            print(pictureNames)


    def convertToJPGSmall(self):
        i=0
        dirs = os.listdir(self.dataSetSmall_path)
        for singleDir in dirs:
            newPath = os.path.join(self.dataSetSmall_path, singleDir)
            pictureNames = os.listdir(newPath)
            for pic in pictureNames:
                img = Image.open(os.path.join(newPath,pic))
                img = img.convert('RGB')
                img.save(os.path.join(self.destPath,"images",str(i)+".jpg"),quality=95)
                boxes = self.datasetSmallDescr[i]["boxes"]
                print(boxes)
                i = i+1
