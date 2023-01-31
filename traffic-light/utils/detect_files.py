import torch
import torchvision
model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='/yolov5/runs/train/exp7/weights/best.pt')

im = "D:\Programmieren\\Uni\Studienarbeit\\test.jpg"

results = model(im)
print(results.pandas().xyxy[0])

results.print()
results.show()  # or .show()


# https://www.vicos.si/resources/dfg/