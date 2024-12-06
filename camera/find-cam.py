#!/usr/bin/env python 

import depthai as dai


def check_cam():

    camera_ip = "192.168.200.193"
    device_info = dai.DeviceInfo(camera_ip)
    with dai.Device(device_info) as device:
        print(f"Successfully connected to the OAK-D PoE camera at {device.getDeviceInfo().name}")


def scan_cam():

    devices = dai.Device.getAllAvailableDevices()

    print(devices)
    # if len(devices) > 0:
    #     for device in devices:
    #         print(f"Found device with IP: {device.getIp()}")
    # else:
    #     print("No devices found. Ensure the camera is connected and powered.")


scan_cam()