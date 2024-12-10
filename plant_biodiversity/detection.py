#!/usr/bin/env python3

from ultralytics import YOLO
import os, cv2, json

def detect_with_yolo(model_filepath, image, custom_classes=None):

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

    annotated_image = result.plot(
        font_size=50, 
        pil=True,
        save=False
    )

    height, width = annotated_image.shape[:2]
    if height > width:
        annotated_image = cv2.rotate(annotated_image, cv2.ROTATE_90_CLOCKWISE)

    return annotated_image, result_list

if __name__ == "__main__":

    # this is the path where this script is located, not where it is executed
    _base_dir_path = os.path.dirname(os.path.realpath(__file__))

    _created_model_filepath = f"{_base_dir_path}/train-validate-results/yolov8_model.pt"
    _test_image_filepath = f"{_base_dir_path}/test-dataset/20240814_103034.jpg"

    _results_filepath = f"{_base_dir_path}/detection-results"
    os.makedirs(_results_filepath, exist_ok=True)

    class_names = ['Plantago', 'Dandelion', 'Feather', 'Bouquet']
    image, data = detect_with_yolo(_created_model_filepath, _test_image_filepath, custom_classes=class_names)

    # save annotated image and data as json file
    file_basename = os.path.splitext(os.path.basename(_test_image_filepath))[0]

    with open(os.path.join(_results_filepath, f"{file_basename}.json"), "w") as json_file:
            json.dump(data, json_file, indent=4)

    cv2.imwrite(os.path.join(_results_filepath, f"{file_basename}.jpg"), image)
    
