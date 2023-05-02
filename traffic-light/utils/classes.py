import os
import multiprocessing as mp
import pathlib
import shutil
import numpy as np
from PIL import Image
import yaml
import json
import cv2


class BoschFilter():
    def __init__(self, basePath: pathlib.Path, dest: pathlib.Path):
        self.trainCount = 0
        self.base_path = basePath
        # convert the yaml to lists for reading the boxes later
        self.destPath = dest
        yaml_path = dest / 'studienarbeit_class_names.yaml'
        self.classTypes = yaml.safe_load(open(yaml_path.resolve()))

    def convertToJPGSmall(self):
        smallPath = self.base_path / 'dataset_additional_rgb' / 'rgb' / 'additional'
        yaml_path = self.base_path / 'dataset_additional_rgb' / 'additional_train.yaml'
        self.converter(smallPath, yaml_path)

    def convertToJPGLarge(self) -> int:
        large_path = self.base_path / 'train_rgb' / 'rgb' / 'train'
        yaml_path = self.base_path / 'train_rgb' / 'train.yaml'
        self.converter(large_path, yaml_path)
        return self.trainCount

    def converter(self, path, yaml_path):
        dataset_descr = yaml.safe_load(open(yaml_path))
        data_set = {}
        # convert it to make it easier to search
        for descr in dataset_descr:
            id = descr["path"][descr["path"].rfind("/") + 1:descr["path"].rfind(".png")]
            data_set[id] = descr["boxes"]
        dataset_descr = data_set
        i = self.trainCount
        dirs = path.iterdir()
        for singleDir in dirs:
            pictureNames = singleDir.iterdir()
            for pic in pictureNames:
                if i % 10 == 0:
                    basePath = self.destPath / 'valid'
                    print(i)
                else:
                    basePath = self.destPath / 'train'
                # get width and height of picture
                try:
                    img = Image.open(pic.resolve())
                    width, height = img.size
                    img.close()
                    # move picture to specific build
                    shutil.copyfile(pic.resolve(), (basePath / 'images' / (str(i) + ".png")).resolve())
                    boxes = dataset_descr[pic.name[:pic.name.find(".")]]
                    with open((basePath / "labels" / (str(i) + ".txt")).resolve(), "w") as f:
                        # each picture if it has labels gets iterated through and the labels are beeing put int o
                        # yolo format
                        for props in boxes:
                            class_id = self.get_class(props["label"])
                            if class_id == -1:
                                continue
                            x_size = props["x_max"] - props["x_min"]
                            y_size = props["y_max"] - props["y_min"]
                            x_center = props["x_min"] + x_size / 2
                            y_center = props["y_max"] + y_size / 2
                            x_size = x_size / width
                            y_size = y_size / height
                            x_center = x_center / width
                            y_center = y_center / height
                            f.write(f'{class_id} {x_center} {y_center} {x_size} {y_size}\n')
                except KeyError:
                    print(pic.name[:pic.name.find(".")] + " not found")
                i += 1
        self.trainCount = i

    def get_class(self, class_name: str) -> int:
        try:
            return list(self.classTypes["names"].values()).index(class_name.lower())
        except:
            return -1


class DTLD():
    def __init__(self, dest_dir: pathlib.Path, src_dir: pathlib.Path, current_count=0):
        self.dest_dir = dest_dir
        # get the last element after sorted the list and get from that the last element (which is automatically the
        # largest and then add 1)
        self.__iterab = current_count
        self.base_dir_to_process = src_dir
        self.yaml_obj = yaml.safe_load((dest_dir / 'studienarbeit_class_names.yaml').open())["names"]

    def read_all_JSON(self):
        json_base = self.base_dir_to_process / 'DTLD_Labels_v2.0' / 'v2.0' / 'DTLD_all.json'
        list_of_elem = json.load(json_base.open())["images"]
        data = []
        for info in list_of_elem:
            data.append([info,self.base_dir_to_process,self.dest_dir,self.__iterab,self.yaml_obj])
            self.__iterab+=1
        print("data acquisition finished")
        with mp.Pool(20) as pool:
           pool.map(DTLD.worker_func,data)
        print("finished with pool")
        return self.__iterab
    @staticmethod
    def worker_func(data):
        info, src, dest, count, yaml_obj = data
        try:
            path_to_img = (src / "Pictures" / info["image_path"][2:]).resolve()
            img_arr = cv2.imread(str(path_to_img), cv2.IMREAD_UNCHANGED)
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
            if count % 10 == 0:
                basePath = dest / 'valid'
            else:
                basePath = dest / 'train'
            with (basePath / "labels" / (str(count) + ".txt")).open(mode='w') as f:
                for label in info["labels"]:
                    class_label = DTLD.determine_class(label["attributes"],yaml_obj)
                    if class_label == -1:
                        continue
                    width = label["w"] / width_img
                    height = label["h"] / height_img
                    x = (label["x"] + label["w"] / 2) / width_img
                    y = (label["y"] + label["h"] / 2) / height_img
                    f.write(f'{class_label} {x} {y} {width} {height}\n')
            img = Image.fromarray(img_arr)
            img.save((basePath / "images" / (str(count) + ".png")).resolve())
        except Exception as e:
            print(e)

    @staticmethod
    def determine_class(attributes,yaml_obj):
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
        return list(yaml_obj.values()).index(class_yaml)
