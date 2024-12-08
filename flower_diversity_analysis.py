#!/usr/bin/env python3

import os, time, cv2, numpy as np
from camera.oak_cam import OakCam
from plant_biodiversity import detection
from plant_coverage import coverage

base_dir_path = os.path.dirname(os.path.realpath(__file__))
class_names = ['Plantago', 'Dandelion', 'Feather', 'Bouquet']
model_filepath = os.path.join(base_dir_path, "plant_diversity/project-results/yolov8_model.pt") 

with OakCam().connect(camera_ip="192.168.200.193") as camera:

    while True:

        image_frame = camera.get_cv_frame()

        # get flower biodiversity data
        out = detection.detect_with_yolo(model_filepath, image_frame, custom_classes=class_names)
        biodiversity_image, xywhn, confidences, classes, class_names = out

        # get plant coverage data
        coverage_image, coverage_percent = coverage.process_image(image_frame)


        both_images = np.concatenate((biodiversity_image, coverage_image), axis=1) 
        cv2.imshow("video", both_images)

        pressed_key = cv2.waitKey(1)
        if pressed_key == ord('q'):
            print("Stopping stream. Bye!")
            break
        
        # elif pressed_key == ord('c'):
        #     saved_image_filepath = f"{base_dir_path}/frame-{int(time.monotonic())}.jpg"
        #     cv2.imwrite(saved_image_filepath, image_frame)
        #     print(f"Frame saved at: {saved_image_filepath}")

cv2.destroyAllWindows()