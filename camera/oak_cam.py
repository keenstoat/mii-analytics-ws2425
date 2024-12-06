#!/usr/bin/env python3

from contextlib import contextmanager
import cv2, os, time
import depthai as dai

class OakCam:

    _VIDEO_STREAM_NAME = "video"

    pipeline = None
    camera_node = None
    video_out_stream = None
    camera_ip = None
    device = None

    def __init__(self):
        
        self.pipeline = dai.Pipeline()

        camera_node = self.pipeline.create(dai.node.ColorCamera)
        camera_node.setBoardSocket(dai.CameraBoardSocket.CAM_A)
        camera_node.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        camera_node.setInterleaved(True)
        camera_node.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.camera_node = camera_node

        video_out_stream = self.pipeline.create(dai.node.XLinkOut)
        video_out_stream.setStreamName(self._VIDEO_STREAM_NAME)
        self.video_out_stream = video_out_stream

        camera_node.video.link(video_out_stream.input)
    
    def search_cam(self):
        devices = dai.Device.getAllAvailableDevices()
        return devices[0].getIp() if devices else None

    @contextmanager
    def connect(self, camera_ip=None):

        self.camera_ip = camera_ip or self.search_cam()
        assert self.camera_ip, "Could not find an available camera in the network"

        with dai.Device(self.pipeline, dai.DeviceInfo(camera_ip)) as device:
            self.device = device
            yield self

    def get_cv_frame(self):

        video_queue = self.device.getOutputQueue(name=self.video_out_stream.getStreamName(), maxSize=1, blocking=False)
        return video_queue.get().getCvFrame()

