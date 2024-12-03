import cv2
import supervision as sv
from ultralytics import YOLO


model = YOLO("D:/Data_Science_Analytics/YOLO_Example/runs2/detect/train/weights/best.pt")

image_path = 'D:/Data_Science_Analytics/YOLO_Example/test/test9.jpg'
image = cv2.imread(image_path)

results = model(image)[0]

detections = sv.Detections.from_ultralytics(results)

detections = detections[detections.confidence > 0.25]

box_annotator = sv.BoxAnnotator(color=sv.Color(0, 255, 0), thickness=5)  # Verde
label_annotator = sv.LabelAnnotator(text_scale=0.3, text_position=sv.Position.TOP_LEFT)

annotated_image = box_annotator.annotate(scene=image, detections=detections)
annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)

save_path = 'D:/Data_Science_Analytics/YOLO_Example/test9_labeled.jpg'
cv2.imwrite(save_path, annotated_image)

image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)  
import matplotlib.pyplot as plt
plt.imshow(image_rgb)
plt.axis('off')  
plt.show()


