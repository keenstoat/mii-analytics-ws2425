#!/usr/bin/env python3

from pathlib import Path
import cv2
import depthai as dai
import numpy as np
import time
from datetime import datetime as dt

# yolo v8 label texts
label_list = [
    "person",         "bicycle",    "car",           "motorbike",     "aeroplane",   "bus",           "train",
    "truck",          "boat",       "traffic light", "fire hydrant",  "stop sign",   "parking meter", "bench",
    "bird",           "cat",        "dog",           "horse",         "sheep",       "cow",           "elephant",
    "bear",           "zebra",      "giraffe",       "backpack",      "umbrella",    "handbag",       "tie",
    "suitcase",       "frisbee",    "skis",          "snowboard",     "sports ball", "kite",          "baseball bat",
    "baseball glove", "skateboard", "surfboard",     "tennis racket", "bottle",      "wine glass",    "cup",
    "fork",           "knife",      "spoon",         "bowl",          "banana",      "apple",         "sandwich",
    "orange",         "broccoli",   "carrot",        "hot dog",       "pizza",       "donut",         "cake",
    "chair",          "sofa",       "pottedplant",   "bed",           "diningtable", "toilet",        "tvmonitor",
    "laptop",         "mouse",      "remote",        "keyboard",      "cell phone",  "microwave",     "oven",
    "toaster",        "sink",       "refrigerator",  "book",          "clock",       "vase",          "scissors",
    "teddy bear",     "hair drier", "toothbrush"
]

sync_nn = True




def create_camera_node(pipeline):
    camera_node = pipeline.create(dai.node.ColorCamera)
    camera_node.setPreviewSize(640, 352) #1080p size
    camera_node.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camera_node.setInterleaved(False)
    camera_node.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    camera_node.setFps(24)

    return camera_node

def create_yolo_detection_node(pipeline):

    # Get yolo v8n model blob file path
    model_path = "/home/charles/repos/data-science/camera/models/yolov8n_coco_640x352.blob"
    if not Path(model_path).exists():
        print(f"Required file not found: {model_path}")
        exit(1)

    detection_node = pipeline.create(dai.node.YoloDetectionNetwork)
    detection_node.setConfidenceThreshold(0.5)
    detection_node.setNumClasses(len(label_list))
    detection_node.setCoordinateSize(4)
    detection_node.setIouThreshold(0.5)
    detection_node.setBlobPath(model_path)
    detection_node.setNumInferenceThreads(2)
    detection_node.input.setBlocking(False)
    return detection_node

def create_camera_stream(pipeline):
    camera_stream = pipeline.create(dai.node.XLinkOut)
    camera_stream.setStreamName("camera_stream")
    return camera_stream

def create_detection_stream(pipeline):
    detection_stream = pipeline.create(dai.node.XLinkOut)
    detection_stream.setStreamName("detection_stream")
    return detection_stream

def normalize_frame_bbox(frame, bbox):
    # nn data, being the bounding box locations, are in <0..1> range - they need to be normalized with frame width/height
    norm_vals = np.full(len(bbox), frame.shape[0])
    norm_vals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * norm_vals).astype(int)

def annotate_frame(frame, detections_list):
    color = (255, 0, 0)
    for detection in detections_list:
        bbox = normalize_frame_bbox(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
        cv2.putText(frame, label_list[detection.label], (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
        cv2.putText(frame, f"{int(detection.confidence * 100)}%", (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

def display_frame(name, frame):
    cv2.imshow(name, frame)

def capture_frame(frame):
    ts = dt.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    image_filename = f"/home/charles/repos/data-science/camera/out/{ts}.jpg"
    cv2.imwrite(image_filename, frame)

def get_next_stream_queue_pair(camera_stream_queue, detection_stream_queue):

    return (camera_stream_queue.get(), detection_stream_queue.get()) \
        if sync_nn else (camera_stream_queue.tryGet(), detection_stream_queue.tryGet())


# Create pipeline ======================================================================================================
pipeline = dai.Pipeline()
camera_node = create_camera_node(pipeline)
detection_node = create_yolo_detection_node(pipeline)
camera_stream = create_camera_stream(pipeline)
detection_stream = create_detection_stream(pipeline)

# Configure inputs and outputs for pipeline nodes ======================================================================
camera_node.preview.link(detection_node.input)
if sync_nn:
    detection_node.passthrough.link(camera_stream.input)
else:
    camera_node.preview.link(camera_stream.input)

detection_node.out.link(detection_stream.input)

# Connect to device and start pipeline =================================================================================
_camera_ip = "192.168.200.193"
device_info = dai.DeviceInfo(_camera_ip)
with dai.Device(pipeline, device_info) as device:

    camera_stream_queue = device.getOutputQueue(name=camera_stream.getStreamName(), maxSize=4, blocking=False)
    detection_stream_queue = device.getOutputQueue(name=detection_stream.getStreamName(), maxSize=4, blocking=False)

    while True:
        camera_element, detection_element = get_next_stream_queue_pair(camera_stream_queue, detection_stream_queue)

        if camera_element is not None:
            frame = camera_element.getCvFrame()
            
            if detection_element is not None:
                annotate_frame(frame, detection_element.detections)
            else:
                print("No detections found!")

            display_frame("Camera", frame)
            if detection_element is not None and detection_element.detections:
                capture_frame(frame)

        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()
