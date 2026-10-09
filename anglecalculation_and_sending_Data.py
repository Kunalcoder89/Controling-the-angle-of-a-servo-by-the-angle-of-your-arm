import cv2
import numpy as np
import mediapipe as mp
import serial
import time
esp32=serial.Serial("/dev/ttyUSB0",115200)
time.sleep(2)
lasttime=0

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = "/home/kunal/Coding/Python/Servo/pose_landmarker_full.task"
angles=[]

base_options = python.BaseOptions(
    model_asset_path=model_path
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options
)

detector = vision.PoseLandmarker.create_from_options(options)

webcam=cv2.VideoCapture(0)

while True:
    succes,img=webcam.read()
    img = cv2.flip(img, 1)
    
    if not succes:
        
        break
    img_RGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    mp_image=mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=img_RGB
    )
    
    results=detector.detect(mp_image)
    if results.pose_landmarks:
        pose=results.pose_landmarks[0]
        shoulder=pose[11]
        elbow=pose[13]
        wrist=pose[15]
        cv2.line(img,(int(shoulder.x*640),int(shoulder.y*480)),(int(elbow.x*640),int(elbow.y*480)),(0,0,255),3)
        cv2.line(img,(int(wrist.x*640),int(wrist.y*480)),(int(elbow.x*640),int(elbow.y*480)),(0,0,255),3)

        
    if cv2.waitKey(1) & 0xFF==ord('q'):
        break
    
    wristpos=np.array([wrist.x*640,wrist.y*480])
    elbowpos=np.array([elbow.x*640,elbow.y*480])
    shoulderpos=np.array([shoulder.x*640,shoulder.y*480])
    v1=shoulderpos-elbowpos
    v2=wristpos-elbowpos
    dotp=np.dot(v1,v2)
    magnitude1 = np.linalg.norm(v1)
    magnitude2=np.linalg.norm(v2)
    cosangle=dotp/(magnitude1*magnitude2)
    angleradian=np.arccos(cosangle)
    angledegree=np.degrees(angleradian)
    angles.append(angledegree)
    if(len(angles)>15):
        angles.pop(0)
    stable_angle=np.mean(angles)
    currenttime=time.time()
    if(currenttime-lasttime>0.05):
         esp32.write(f"{stable_angle:.0f}\n".encode())
        lasttime=currenttime
    
    # print(angledegree)
    img=cv2.flip(img,1)
    cv2.putText(
    img,
    f"Angle: {angledegree:.1f}",
    (30, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
    )   
    
    cv2.imshow("Webcam",img)

webcam.release()
cv2.destroyAllWindows()
