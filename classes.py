import os
from PIL import Image
import yaml





class BoschFilter():
    def __init__(self,basePath,dest):
        self.trainCount =0
        self.validCount =0
        self.dataSetSmall_path = os.path.join(os.path.realpath(basePath), "dataset_additional_rgb")
        self.datasetLarge_path = os.path.join(os.path.realpath(basePath), "train_rgb")
        # convert the yaml to lists for reading the boxes later
        self.datasetLargeDescr = yaml.safe_load(open(os.path.join(self.datasetLarge_path, "train.yaml")))
        self.datasetSmallDescr = yaml.safe_load(open(os.path.join(self.dataSetSmall_path, "additional_train.yaml")))
        # get to the data check
        self.dataSetSmall_path = os.path.join(self.dataSetSmall_path, "rgb", "additional")
        small = {}
        # convert it to make it easier to search
        for descr in self.datasetSmallDescr:
            id = descr["path"][descr["path"].rfind("/")+1:descr["path"].rfind(".png")]
            small[id] = descr["boxes"]
        self.datasetSmallDescr = small
        print(small)
        self.datasetLarge_path = os.path.join(self.datasetLarge_path, "rgb", "train")

        self.destPath = dest
        self.classTypes = yaml.safe_load(open("./trafficLightsAndSigns.yaml"))

    def convertToJPGLarge(self):

        dirs = os.listdir(self.datasetLarge_path)
        for singleDir in dirs:
            newPath =os.path.join(self.datasetLarge_path,singleDir)
            pictureNames = os.listdir(newPath)
            print(pictureNames)


    def convertToJPGSmall(self):
        i = self.trainCount
        dirs = os.listdir(self.dataSetSmall_path)
        for singleDir in dirs:
            newPath = os.path.join(self.dataSetSmall_path, singleDir)
            pictureNames = os.listdir(newPath)
            for pic in pictureNames:
                try:
                    boxes = self.datasetSmallDescr[pic[:pic.find(".")]]
                    img = Image.open(os.path.join(newPath, pic))
                    img = img.convert('RGB')
                    width, height = img.size
                    basePath = ""
                    if i % 10 == 0:
                        basePath = os.path.join(self.destPath,"..","valid")
                    else:
                        basePath = self.destPath
                    img.save(os.path.join(basePath, "images", str(i) + ".jpg"), quality=95)
                    with open(os.path.join(basePath,"label",str(i)+".txt"),"w") as f:
                        textline = ""
                        # each picture if it has labels gets iterated through and the labels are beeing put int o
                        # yolo format
                        for props in boxes:
                            val = self.get_class(props["label"])
                            if val == -1:
                                continue
                            x_size = props["x_max"]-props["x_min"]
                            y_size = props["y_max"]-props["y_min"]
                            x_center =props["x_min"]+ x_size/2
                            y_center = props["y_max"]+ y_size/2
                            x_size = x_size/width
                            y_size = y_size/height
                            x_center = x_center/width
                            y_center = y_center/height
                            f.write(str(val)+" "+str(x_center)+" "+str(y_center)+" "+str(x_size)+" "+str(y_size)+"\n")
                    i = i + 1
                except Exception as ex:
                    print(ex)
                    print("missing: " +pic)
        self.trainCount= i

    def get_class(self,className:str)->int:
        try:
            return list(self.classTypes["names"].values()).index(className.lower())
        except:
            return -1