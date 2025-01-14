from ultralytics import YOLO

model = YOLO("models/yolo11_best.pt")

# test
test_results = model(['data/test_1.jpg', 'data/test_2.jpg'])

for result in test_results:

    result.show()