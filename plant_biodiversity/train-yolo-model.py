#!/usr/bin/env python3

from ultralytics import YOLO
import os, shutil
import os
import random
import shutil
from yaml import safe_dump as yaml_dump


# Create a data set random split to train model ========================================================================

def split_dataset(source_dir, percentage=0.8):

    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    all_img_files = [
        filename for filename in os.listdir(source_dir)
        if filename.lower().endswith('.jpg') and os.path.isfile(os.path.join(source_dir, filename))
    ]

    num_files_to_copy = int(len(all_img_files) * percentage)

    training_files = random.sample(all_img_files, num_files_to_copy)
    validation_files = [filename for filename in all_img_files if filename not in training_files]
    
    assert len(all_img_files) == len(training_files) + len(validation_files)

    return training_files, validation_files

def copy_files(img_base_filename_list, source_dir, yolo_base_dir, train_or_val_dir):

    os.makedirs(os.path.join(yolo_base_dir, f"images/{train_or_val_dir}"), exist_ok=True)
    os.makedirs(os.path.join(yolo_base_dir, f"labels/{train_or_val_dir}"), exist_ok=True)

    for img_base_filename in img_base_filename_list:
        basename, _ = os.path.splitext(img_base_filename)
        ann_base_filename = f"{basename}.txt"

        src_img_path = os.path.join(source_dir, img_base_filename)
        dest_img_path = os.path.join(yolo_base_dir, f"images/{train_or_val_dir}", img_base_filename)

        src_ann_path = os.path.join(source_dir, ann_base_filename)
        dest_ann_path = os.path.join(yolo_base_dir, f"labels/{train_or_val_dir}", ann_base_filename)

        shutil.copy(src_img_path, dest_img_path)
        if os.path.isfile(src_ann_path):
            shutil.copy(src_ann_path, dest_ann_path)
        else:
            with open(dest_ann_path, 'w') as _: pass

def create_yolo_dataset(source_dir, yolo_dataset_dir, yolo_config_filepath):

    print(f"Deleting YOLO dataset root dir: {yolo_dataset_dir}")
    if os.path.isdir(yolo_dataset_dir):
        shutil.rmtree(yolo_dataset_dir)
    
    print("Randomly spliting dataset for training and validation")
    training_files, validation_files = split_dataset(source_dir, percentage=0.8)

    print(f"- Training files:     {len(training_files)}")
    print(f"- Validation files:   {len(validation_files)}")

    print("Copying training files...")
    copy_files(training_files, source_dir, yolo_dataset_dir, "train")
    assert len(os.listdir(os.path.join(yolo_dataset_dir, "images/train"))) == len(training_files), \
        "training files count does not match"
    
    print("Copying validation files...")
    copy_files(validation_files, source_dir, yolo_dataset_dir, "val")
    assert len(os.listdir(os.path.join(yolo_dataset_dir, "images/val"))) == len(validation_files), \
        "validation files count does not match"

    detection_class_list = [
        "Plantago lanceolata - White",
        "Dandelion or similar - yellow",
        "White feather spike",
        "bouquet white flower",
    ]

    dataset_dict = {
        "path": yolo_dataset_dir,
        "train": "images/train",
        "val": "images/val",
        "nc": len(detection_class_list),
        "names": detection_class_list
    }
    print("Creating YOLO config file")
    with open(yolo_config_filepath, 'w') as yaml_file:
        yaml_dump(dataset_dict, yaml_file, default_flow_style=False)

# Train and validate model =============================================================================================

def train_model(train_parameters:dict, model_filepath):
    print("TRAIN MODEL ===============================================================================================")
    print("===========================================================================================================")

    project_name = train_parameters["project"]
    os.makedirs(project_name, exist_ok=True)

    pretrained = train_parameters["pretrained"]
    if pretrained:
        assert model_filepath, f"Base model missing at '{model_filepath}'. It is needed to re-train the model"
        model = YOLO(model_filepath)
    else:
        model = YOLO("yolov8n.pt") # TODO check if nano model is ok

    model_name = train_parameters.get("name", "yolov8_model") + "train"
    
    model.train(
        data=train_parameters["data"],
        pretrained=pretrained,
        exist_ok=train_parameters.get("exist_ok", True),
        imgsz=train_parameters.get("imgsz", 640),
        epochs=train_parameters.get("epochs", 10),
        batch=train_parameters.get("batch", 5),
        project=project_name,
        name=model_name,
    )

    best_model_filepath = f"{project_name}/{model_name}/weights/best.pt"
    shutil.copyfile(best_model_filepath, model_filepath)

def validate_model(train_parameters:dict, model_filepath):

    print("VALIDATE MODEL ============================================================================================")
    print("===========================================================================================================")

    assert os.path.isfile(model_filepath), f"Model file does not exist at {model_filepath}"

    model = YOLO(model_filepath)
    model.val(
        data=train_parameters["data"],
        project=train_parameters["project"],
        name=train_parameters.get("name", "yolov8_model") + "val",
        exist_ok=train_parameters.get("exist_ok", True),
    )


if __name__ == "__main__":

    # the base path is ALWAYS the directory where this script is contained
    _base_dir_path = os.path.dirname(os.path.realpath(__file__))
    _base_dir_path = os.path.abspath(_base_dir_path)

    _original_dataset_dir = f"{_base_dir_path}/original-dataset"
    _test_dataset_dir = f"{_base_dir_path}/test-dataset"

    _yolo_dataset_dir = f"{_base_dir_path}/yolo-dataset"
    _yolo_config_filepath = f"{_yolo_dataset_dir}/data.yaml"

    _results_dir = f"{_base_dir_path}/train-validate-results"
    _created_model_filepath = f"{_results_dir}/yolov8_model.pt"

    _yolo_train_parameters = {
        "data":         _yolo_config_filepath,
        "pretrained":   False,
        "exist_ok":     True,
        "imgsz":        640,
        "epochs":       50,
        "batch":        3,
        "augment":      True, # TODO check this
        "project":      _results_dir
    }

    create_yolo_dataset(_original_dataset_dir, _yolo_dataset_dir, _yolo_config_filepath)
    train_model(_yolo_train_parameters, _created_model_filepath)
    validate_model(_yolo_train_parameters, _created_model_filepath)
