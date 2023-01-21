import torch
import torchvision
model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='D:\Programmieren\\Uni\Studienarbeit\yolov5\\runs\\train\exp4\weights\\best.pt')

im = "D:\Programmieren\\Uni\Studienarbeit\\test.jpg"

results = model(im)
print(results.pandas().xyxy[0])

results.print()
results.save()  # or .show()