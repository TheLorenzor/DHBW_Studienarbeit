import pathlib
import csv
import shutil
from classes import BoschFilter, DTLD

def convert_GTSRB(type_data:str,incr:int,current_count:int):
    path = pathlib.Path(__file__).parent.parent.parent / 'data'
    csv_path_train = path / 'Rohdaten' / 'GTSRB' / (type_data+'.csv')
    # dir is build <id of GTRSB Data set>:<My Own ID>
    dict_of_classes = {1: 12, 4: 13, 13: 15, 14: 14, 15: 18, 17: 16, 18: 19, 25: 17, 27: 21}
    if type_data == 'Train':
        type_data = 'train'
    else:
        type_data = 'valid'
    with open(csv_path_train.resolve(), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        count = 0
        for row in reader:
            if count == 0:
                count += 1
                continue
            # only work with the given files
            if int(row[6]) in (1, 4, 13, 14, 15, 17, 18, 25, 27):
                width_img = int(row[4]) - int(row[2])
                height_img = int(row[5]) - int(row[3])
                width_yolo = width_img / int(row[0])
                height_yolo = height_img / int(row[1])
                center_x = (int(row[2]) + (width_img / 2)) / int(row[0])
                center_y = (int(row[3]) + (width_img / 2)) / int(row[1])
                class_id = dict_of_classes[int(row[6])]
                dest_path_img = path / 'data' / type_data / 'images' / (str(current_count) + '.png')
                src_path = csv_path_train.parent / row[7]
                shutil.copyfile(src_path, dest_path_img)
                dest_path_lab = path / 'data' / type_data / 'labels' / (str(current_count) + '.txt')
                with open(dest_path_lab, 'x') as f:
                    f.write(f'{class_id} {center_x} {center_y} {width_yolo} {height_yolo}\n')
                current_count += incr

            count += 1
    return current_count

if __name__ =="__main__":
    base_path = pathlib.Path(__file__).parent.parent.parent / 'data'
    bosch_path = base_path / 'Rohdaten' / 'Bosch Training Dataset'
    dest_path = base_path / 'data'
    bosch = BoschFilter(bosch_path,dest_path)
    current_count = bosch.convertToJPGLarge()
    print("Bosch Traffic Lights Finished")
    daimler = DTLD(base_path/'data',bosch_path.parent / 'DTLD',current_count)
    current_count = daimler.read_all_JSON()
    print("Daimler Traffic Lights Finished")
    current_count = convert_GTSRB('Train',1,current_count)

    current_count = current_count- (current_count % 10)+10
    print("Train Traffic Signs Finished")
    convert_GTSRB('Test',10,current_count)
    print("Validate Traffic Signs Finished")
    print("Finished")