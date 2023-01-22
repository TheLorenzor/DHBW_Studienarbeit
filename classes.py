import os
import numpy as np
from PIL import Image
import yaml
import json
import cv2


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
        self.converter(smallPath, yaml_path)

    def convertToJPGLarge(self):
        large_path = os.path.join(os.path.realpath(self.base_path), "train_rgb", "rgb", "train")
        yaml_path = os.path.join(self.base_path, "train_rgb", "train.yaml")
        self.converter(large_path, yaml_path)

    def converter(self, path, yaml_path):
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


class DTLD():
    def __init__(self):

        self.base_dir_target = os.path.join("datasets", "trafficlights")
        all_imgs = os.listdir(os.path.join("datasets", "trafficlights", "train", "images"))
        all_imgs.sort(key=lambda x: int(x[:x.index(".")]))
        # get the last element after sorted the list and get from that the last element (which is automatically the
        # largest and then add 1)
        self.__iterab = int(all_imgs[len(all_imgs) - 1][:all_imgs[len(all_imgs) - 1].index(".")]) + 1
        self.base_dir_to_process = os.path.join("datasets", "Rohdaten", "DTLD")
        self.yaml_obj = yaml.safe_load(open("trafficLightsAndSigns.yaml"))["names"]

    def read_all_JSON(self):
        json_base = os.path.join(self.base_dir_to_process, "DTLD_Labels_v2.0", "v2.0", "DTLD_all.json")
        list_of_elem = json.load(open(json_base))["images"]
        for info in list_of_elem:
            # reads it as unchanged thread of data
            img_arr = cv2.imread(os.path.join(self.base_dir_to_process, "Pictures", info["image_path"][2:]),
                                 cv2.IMREAD_UNCHANGED)
            # converts it via the  bayer filter into an rgb image
            img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BAYER_GB2BGR)
            img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
            img_arr = np.right_shift(img_arr, 4)
            # set the right tones (convert to 8bit from 12 bit)
            img_arr = img_arr.astype(np.uint8)
            # get height of the image for calculation in relation
            height_img = img_arr.shape[0]
            width_img = img_arr.shape[1]
            x = 0
            y = 0
            with open(os.path.join(self.base_dir_target, "train", "labels", str(self.__iterab) + ".txt"), "w") as f:
                for label in info["labels"]:
                    class_label = self.determine_class(label["attributes"])
                    if class_label == -1:
                        continue
                    width = label["w"] / width_img
                    height = label["h"] / height_img
                    x = (label["x"] + label["w"] / 2) / width_img
                    y = (label["y"] + label["h"] / 2) / height_img
                    f.write(
                        str(class_label) + " " + str(x) + " " + str(y) + " " + str(width) + " " + str(
                            height) + "\n")
            img = Image.fromarray(img_arr)
            img.save(os.path.join(self.base_dir_target, "train", "images", str(self.__iterab) + ".jpg"))
            self.__iterab += 1
            if self.__iterab%10 ==0:
                print(self.__iterab)

    def determine_class(self, attributes):
        if attributes["state"] == "off" or attributes["state"] == "unknown" or attributes["reflection"] == "reflected":
            return -1
        class_yaml = attributes["state"]
        if class_yaml == "red_yellow":
            class_yaml = "red"
        if attributes["pictogram"] == "arrow left":
            class_yaml = class_yaml + "left"
        elif attributes["pictogram"] == "arrow straight":
            class_yaml = class_yaml + "straight"
        elif attributes["pictogram"] == "arrow right":
            class_yaml = class_yaml + "right"
        elif attributes["pictogram"] == "circle":
            pass
        else:
            return -1
        return list(self.yaml_obj.values()).index(class_yaml)
