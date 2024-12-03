
## Comando para entrenar el modelo
## yolo train data=D:/Data_Science_Analytics/YOLO_Example/data.yaml model=yolov8s.pt epochs=50 batch=3 imgsz=640 augment=True


from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Ruta al modelo entrenado
weights_path = 'D:/Data_Science_Analytics/YOLO_Example/runs2/detect/train/weights/best.pt'

# Ruta de la imagen a procesar
image_path = 'D:/Data_Science_Analytics/YOLO_Example/test/test11.jpg'

model = YOLO(weights_path)

results = model(image_path)

results[0].show() 

results[0].save()  


image = cv2.imread(results[0].paths[0]) 
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir BGR a RGB

plt.imshow(image)
plt.axis('off')  
plt.show()

