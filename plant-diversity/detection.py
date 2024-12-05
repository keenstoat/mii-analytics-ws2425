#!/usr/bin/env python3

from ultralytics import YOLO
import os, cv2, json
from matplotlib import pyplot as plt
import supervision as sv
from contextlib import redirect_stdout as to_stdout

def show_images(*images):

    for image in images:
        image = cv2.resize(image, (0, 0), fx = 0.3, fy = 0.3)
        cv2.imshow("Results", image)

        cv2.waitKey(0)
        
    cv2.destroyAllWindows()

def detect_with_yolo(model_filepath, image, custom_classes=None, class_colors=None):

    
    assert os.path.isfile(model_filepath), f"Model file does not exist at {model_filepath}"

    model = YOLO(model_filepath, task="detect")

    if custom_classes:
        model.model.names = custom_classes

    result = model(image)[0]
    boxes = result.boxes.numpy()

    result_list = []
    for bbox, conf, class_id in zip(boxes.xywhn, boxes.conf, boxes.cls):
        class_id = int(class_id)
        result_list.append({
            "name": result.names[class_id],
            "class": class_id,
            "confidence": round(float(conf), 6),
            "box": {
                "x": round(float(bbox[0]), 6),
                "y": round(float(bbox[1]), 6),
                "w": round(float(bbox[2]), 6),
                "h": round(float(bbox[3]), 6)
            }
        })
    with open(f"detection/result.json", "w") as json_file:
        json.dump(result_list, json_file, indent=4)

    if class_colors:
        class_colors = dict(zip(result.names, class_colors))
    
    annotated_image = result.plot(
        font_size=50, 
        pil=True,
        save=True,
        filename="detection/result.jpg"
    )

    return annotated_image, boxes.xywhn, boxes.conf, boxes.cls, result.names

def detect_with_sv(model_filepath, image):
    
    model = YOLO(model_filepath)
    if type(image) == str:
        image = cv2.imread(image)

    results = model(image)[0]

    detections = sv.Detections.from_ultralytics(results)

    # detections = detections[detections.confidence > 0.25]

    box_annotator = sv.BoxAnnotator(color=sv.Color(0, 255, 0), thickness=5)
    label_annotator = sv.LabelAnnotator(text_scale=0.3, text_position=sv.Position.TOP_LEFT)

    annotated_image = box_annotator.annotate(scene=image, detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)

    return annotated_image




_base_dir_path = os.path.dirname(os.path.realpath(__file__))

_created_model_filepath = f"{_base_dir_path}/project-results/yolov8_model.pt"
_test_image_filepath = f"{_base_dir_path}/test-dataset/20240814_103034.jpg"

class_names = ['Plantago', 'Dandelion', 'Feather', 'Bouquet']
class_colors = ['red', 'yellow', 'blue', 'green']
out = detect_with_yolo(_created_model_filepath, _test_image_filepath, custom_classes=class_names, class_colors=class_colors)
image_a, xyxy_list, confidences, classes, class_names = out

# show_images(image_a)
# show_images(detect_with_sv(_created_model_filepath, _test_image_filepath))
