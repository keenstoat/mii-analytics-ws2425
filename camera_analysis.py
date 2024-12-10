#!/usr/bin/env python3

from os.path import join as join_path
import sys, os, json, cv2, numpy as np
from camera.oak_cam import OakCam
from plant_biodiversity import detection
from plant_coverage import coverage


base_dir_path = os.path.dirname(os.path.realpath(__file__))
class_names = ['Plantago', 'Dandelion', 'Feather', 'Bouquet']
model_filepath = join_path(base_dir_path, "plant_biodiversity/train-validate-results/yolov8_model.pt") 

window_name = "Biodiversity - Coverage"

def live_processing():

    with OakCam().connect(camera_ip="192.168.200.193") as camera:
        
        print("Connected to the camera!")
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE) 
        while True:

            # close windows when clicking on the close button
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                print("Stopping stream. Bye!")
                break
            
            try:
                image_frame = camera.get_cv_frame()
                biodiversity_image = detection.detect_with_yolo(model_filepath, image_frame, custom_classes=class_names)[0]
                coverage_image = coverage.process_image(image_frame)[0]

                image_a = cv2.resize(biodiversity_image, (832, 624))
                image_b = cv2.resize(coverage_image, (832, 624))
                both_images = np.concatenate((image_a, image_b), axis=1) 
                cv2.imshow(window_name, both_images)
                
            except Exception as ex:
                print("Something went wrong: ")
                print(ex)
                # exit()

            pressed_key = cv2.waitKey(1)
            if pressed_key == ord('q'):
                print("Stopping stream. Bye!")
                break

        cv2.destroyAllWindows()

def live_processing_mock():

    dirr = "/home/charles/repos/mii-analytics-ws2425/plant_biodiversity/original-dataset"
    
    print("Connected to the camera!")
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE) 
    do = True
    while do:

        for path in os.listdir(dirr):
            if not path.endswith(".jpg"):
                continue
            # close windows when clicking on the close button
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                print("Stopping stream. Bye!")
                do = False
                break
            
            image_frame = cv2.imread(f"{dirr}/{path}")
            biodiversity_image, _ = detection.detect_with_yolo(model_filepath, image_frame, custom_classes=class_names)
            coverage_image = coverage.process_image(image_frame)[0]

            image_a = cv2.resize(biodiversity_image, (832, 624))
            image_b = cv2.resize(coverage_image, (832, 624))
            both_images = np.concatenate((image_a, image_b), axis=1) 
            cv2.imshow(window_name, both_images)

            pressed_key = cv2.waitKey(1)
            if pressed_key == ord('q'):
                print("Stopping stream. Bye!")
                do = False
                break

    cv2.destroyAllWindows()



def one_shot_processing(save_path, preview=False):

    if not save_path:
        print("Must define a path to save results")
        return
    os.makedirs(save_path, exist_ok=True)

    with OakCam().connect(camera_ip="192.168.200.193") as camera:
        print("Connected to the camera!")

        # discard the first 10 frames - these are blurry and not good for processing
        for _ in range(10):
            camera.get_cv_frame()

        image_frame = camera.get_cv_frame()

        # get biodiversity data from image and save it
        biodiversity_image, biodiversity_data = detection.detect_with_yolo(model_filepath, image_frame, custom_classes=class_names)
        cv2.imwrite(join_path(save_path, "biodiversity-detection.jpg"), biodiversity_image)
        with open(join_path(save_path, "biodiversity-detection.json"), "w") as out_file:
            json.dump(biodiversity_data, out_file, indent=4)
        
        coverage_image, coverage_data = coverage.process_image(image_frame)
        cv2.imwrite(join_path(save_path, "coverage-detection.jpg"), coverage_image)
        with open(join_path(save_path, "coverage-detection.json"), "w") as out_file:
            json.dump(coverage_data, out_file, indent=4)

        print(f"Results saved at: {save_path}")

        if preview:
            biodiversity_image = cv2.resize(biodiversity_image, (832, 624))
            coverage_image = cv2.resize(coverage_image, (832, 624))
            both_images = np.concatenate((biodiversity_image, coverage_image), axis=1) 
            cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE) 
            while True:
                if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                    print("Stopping stream. Bye!")
                    break
            
                cv2.imshow(window_name, both_images)
                if cv2.waitKey(1) == ord('q'):
                    break
            cv2.destroyAllWindows()

def one_shot_processing_mock(save_path, preview=False):

    if not save_path:
        print("Must define a path to save results")
        return
    os.makedirs(save_path, exist_ok=True)

    dirr = "/home/charles/repos/mii-analytics-ws2425/plant_biodiversity/original-dataset/20240814_102705.jpg"

    print("Connected to the camera!")

    image_frame = cv2.imread(dirr)

    # get biodiversity data from image and save it
    biodiversity_image, biodiversity_data = detection.detect_with_yolo(model_filepath, image_frame, custom_classes=class_names)
    cv2.imwrite(join_path(save_path, "biodiversity-detection.jpg"), biodiversity_image)
    with open(join_path(save_path, "biodiversity-detection.json"), "w") as out_file:
        json.dump(biodiversity_data, out_file, indent=4)
    
    coverage_image, coverage_data = coverage.process_image(image_frame)
    cv2.imwrite(join_path(save_path, "coverage-detection.jpg"), coverage_image)
    with open(join_path(save_path, "coverage-detection.json"), "w") as out_file:
        json.dump(coverage_data, out_file, indent=4)

    print(f"Results saved at: {save_path}")

    if preview:
        biodiversity_image = cv2.resize(biodiversity_image, (832, 624))
        coverage_image = cv2.resize(coverage_image, (832, 624))
        both_images = np.concatenate((biodiversity_image, coverage_image), axis=1) 
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE) 
        while True:
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                print("Stopping stream. Bye!")
                break
        
            cv2.imshow(window_name, both_images)
            if cv2.waitKey(1) == ord('q'):
                break
        cv2.destroyAllWindows()


if __name__ == "__main__":

    _args = sys.argv.copy()
    _script_name = os.path.basename(_args.pop(0))
    
    _action = _args.pop(0) if _args else None
    
    if _action == "live":
        live_processing()

    elif _action == "livemock":
        live_processing_mock()

    elif _action == "once":
        _save_path = _args.pop(0) if _args else None
        one_shot_processing(_save_path, preview=True)
    
    elif _action == "oncemock":
        _save_path = _args.pop(0) if _args else None
        one_shot_processing_mock(_save_path, preview=True)
        
    else:
        print(f"Action '{_action}' not recognized.")
        exit(1)
