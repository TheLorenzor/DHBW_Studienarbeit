import pathlib
import csv
import os
# start by 46285 --> the next one
"""
-1: 30 Limit Schild
-4: 70 Limit Schild
-14: Stop
-13: Vorfahrt gewähren
-17: Verbot einfahrt
25: Baustelle
- 15: VerbotAlleFahrzeuge
-18: Gefahrstelle
--: Gehweg
27: Fußgangueberweg
"""


def del_non_rel_test():
    path = pathlib.Path(__file__).parent.parent.parent / 'data' / 'Rohdaten_Signs'
    test_path = path / 'Test.csv'
    with open(test_path.resolve(), newline='') as csvfile:
        reader = csv.reader(csvfile,delimiter=',')
        count = 0
        for row in reader:
            if count==0:
                count += 1
                continue
            class_id =int(row[6])
            if class_id not in (1,4,13,14,15,17,18,25,27):
                path_to_file = row[7]
                file_path = path / path_to_file
                os.remove(file_path)
                print(str(class_id)+"--"+str(row[7]))

