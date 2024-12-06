#!/usr/bin/env python3

import cv2
import numpy as np
import requests

# URL of the image
def get_image(session):

    with session.get(url, stream=True) as response:
        if response.status_code == 200:
            image_array = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image

def get_session():
    with requests.Session() as session:
        return session

url = "http://172.21.128.1:8000"


session = get_session()


while True:
    image = get_image(session)
    # with session.get(url, stream=True) as response:
    #     if response.status_code == 200:

    #         image_array = np.frombuffer(response.content, np.uint8)
    #         img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            

    cv2.imshow("Image from Server", image)
    
    pressed_key = cv2.waitKey(1)
    if pressed_key == ord('q'):
        break

cv2.destroyAllWindows()
