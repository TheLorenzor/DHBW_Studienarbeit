import os
from PIL import Image
import yaml


class BoschFilter():
    def __init__(self, basePath, dest):
        self.trainCount = 0
        self.validCount = 0
        self.base_path = basePath
        # convert the yaml to lists for reading the boxes later
        self.datasetDescr = yaml.safe_load(
            open(os.path.join(basePath, "dataset_additional_rgb", "additional_train.yaml")))
        small = {}
        # convert it to make it easier to search
        for descr in self.datasetDescr:
            id = descr["path"][descr["path"].rfind("/") + 1:descr["path"].rfind(".png")]
            small[id] = descr["boxes"]
        self.datasetDescr = small
        self.destPath = dest
        self.classTypes = yaml.safe_load(open("./trafficLightsAndSigns.yaml"))

    def convertToJPGSmall(self):
        smallPath = os.path.join(os.path.realpath(self.base_path), "dataset_additional_rgb", "rgb", "additional")
        yaml_path = os.path.join(self.base_path, "dataset_additional_rgb", "additional_train.yaml")
        self.converter(smallPath,yaml_path)

    def convertToJPGLarge(self):
        large_path = os.path.join(os.path.realpath(self.base_path), "train_rgb", "rgb", "train")
        yaml_path = os.path.join(self.base_path, "train_rgb", "train.yaml")
        self.converter(large_path, yaml_path)



    def converter(self,path,yaml_path):
        dataset_descr = yaml.safe_load(open(yaml_path))
        small = {}
        # convert it to make it easier to search
        for descr in dataset_descr:
            id = descr["path"][descr["path"].rfind("/") + 1:descr["path"].rfind(".png")]
            small[id] = descr["boxes"]
        dataset_descr = small
        i = self.trainCount
        dirs = os.listdir(path)
        for singleDir in dirs:
            newPath = os.path.join(path, singleDir)
            pictureNames = os.listdir(newPath)
            for pic in pictureNames:
                try:
                    boxes = dataset_descr[pic[:pic.find(".")]]

                    img = Image.open(os.path.join(newPath, pic))
                    img = img.convert('RGB')
                    width, height = img.size
                    basePath = ""
                    if i % 10 == 0:
                        basePath = os.path.join(self.destPath, "..", "valid")
                    else:
                        basePath = self.destPath
                    img.save(os.path.join(basePath, "images", str(i) + ".jpg"), quality=95)

                    with open(os.path.join(basePath, "label", str(i) + ".txt"), "w") as f:
                        textline = ""
                        # each picture if it has labels gets iterated through and the labels are beeing put int o
                        # yolo format
                        for props in boxes:
                            val = self.get_class(props["label"])
                            if val == -1:
                                continue
                            x_size = props["x_max"] - props["x_min"]
                            y_size = props["y_max"] - props["y_min"]
                            x_center = props["x_min"] + x_size / 2
                            y_center = props["y_max"] + y_size / 2
                            x_size = x_size / width
                            y_size = y_size / height
                            x_center = x_center / width
                            y_center = y_center / height
                            f.write(
                                str(val) + " " + str(x_center) + " " + str(y_center) + " " + str(x_size) + " " + str(
                                    y_size) + "\n")
                    i = i + 1
                except Exception as ex:
                    print(ex)
                    print("missing: " + pic)
        self.trainCount = i

    def get_class(self, class_name: str) -> int:
        try:
            return list(self.classTypes["names"].values()).index(class_name.lower())
        except:
            return -1