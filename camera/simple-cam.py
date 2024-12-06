#!/usr/bin/env python 


import depthai as dai
import cv2
import time

# Create a pipeline
pipeline = dai.Pipeline()

# Define a color camera node
cam_rgb = pipeline.createColorCamera()
x_out_video = pipeline.createXLinkOut()

x_out_video.setStreamName("video")
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
cam_rgb.preview.link(x_out_video.input)

# Connect to the camera
# Specify the camera's IP address
_camera_ip = "192.168.200.193"
device_info = dai.DeviceInfo(_camera_ip)
with dai.Device(pipeline, device_info) as device:
    print(f"Connected to the OAK-D PoE camera at {_camera_ip}")

    video_queue = device.getOutputQueue(name=x_out_video.getStreamName(), maxSize=4, blocking=False)

    while True:
        # Get a frame
        frame = video_queue.get().getCvFrame()

        # Display the frame
        cv2.imshow("OAK-D PoE Camera", frame)

        pressed_key = cv2.waitKey(1)
        if pressed_key == ord('q'):
            break
        
        elif pressed_key == ord('c'):
            cv2.imwrite(f"/home/charles/repos/data-science/camera/out/frame-{int(time.monotonic())}.jpg", frame)

    cv2.destroyAllWindows()




