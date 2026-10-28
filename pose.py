from ultralytics import YOLO

model = YOLO("yolo26n-pose.pt")

for result in model.predict(source=0, show=True, stream=True):
    pass