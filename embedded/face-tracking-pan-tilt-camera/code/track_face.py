# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 18:03:22 2018

@author: James Wu
"""

import cv2
import numpy as np
import serial
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
cascade_path = os.path.join(script_dir, 'data', 'haarcascade_frontalface_default.xml')

face_cascade = cv2.CascadeClassifier(cascade_path)

# Verify that the cascade file loaded successfully
if face_cascade.empty():
    print(f"Error: Could not load cascade classifier from {cascade_path}")
    print("Please check if the file exists and is accessible.")
    exit()

#==============================================================================
#   1.多人脸形心检测函数 (Improved Detection Algorithm)
#       输入：视频帧
#       输出：各人脸总形心坐标
#==============================================================================
def Detection(frame):
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)  #转换为灰度图
    
    # Apply histogram equalization to improve contrast
    gray = cv2.equalizeHist(gray)
    
    # Improved face detection with better parameters
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1,  # Smaller scale factor for better detection
        minNeighbors=6,   # Higher value to reduce false positives
        minSize=(30, 30), # Minimum face size
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    if len(faces) > 0: 
        # Filter faces by size to remove very small detections
        filtered_faces = []
        for (x, y, w, h) in faces:
            if w > 50 and h > 50:  # Only keep faces larger than 50x50
                filtered_faces.append((x, y, w, h))
        
        if len(filtered_faces) > 0:
            # Find the biggest face (by area)
            biggest_face = max(filtered_faces, key=lambda face: face[2] * face[3])
            x, y, w, h = biggest_face
            
            # Draw only the biggest face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            X = x + w // 2
            Y = y + h // 2
            center_pt = (X, Y)   #人脸中点坐标
            cv2.circle(frame, center_pt, 8, (0, 0, 255), -1)   #绘制人脸中点
            
            # Use the biggest face center as the centroid
            centroid_X = X
            centroid_Y = Y
            centroid_pt = (centroid_X, centroid_Y)   #人脸形心坐标
            cv2.circle(frame, centroid_pt, 12, (255, 0, 0), -1)   #绘制人脸形心 (larger blue circle)
        else:
            centroid_X = 320
            centroid_Y = 240
    else:
        centroid_X = 320
        centroid_Y = 240
    #==========================================================================
    #     绘制参考线
    #==========================================================================
    x = 0;
    y = 0;
    w = 320;
    h = 240;
    
    rectangle_pts = np.array([[x,y],[x+w,y],[x+w,y+h],[x,y+h]], np.int32) #最小包围矩形各顶点
    cv2.polylines(frame, [rectangle_pts], True, (0,255,0), 2) #绘制最小包围矩形
    
    x2 = 320;
    y2 = 240;
    rectangle_pts2 = np.array([[x2,y2],[x2+w,y2],[x2+w,y2+h],[x2,y2+h]], np.int32) #最小包围矩形各顶点
    cv2.polylines(frame, [rectangle_pts2], True, (0,255,0), 2) #绘制最小包围矩形

    #==========================================================================
    #     显示
    #==========================================================================
    cv2.imshow('frame',frame)
    
    return centroid_X,centroid_Y
                
#==============================================================================
#   ****************************主函数入口***********************************
#==============================================================================

# 设置串口参数
ser = serial.Serial()
ser.baudrate = 115200    # 设置比特率为115200bps
ser.port = '/dev/tty.usbmodem48CA435ED2642'

# Try to open serial port with error handling
try:
    ser.open()             # 打开串口
    print("Serial port opened successfully")
    
    #先发送一个中心坐标使初始化时云台保持水平
    data = '#'+str('320')+'$'+str('240')+'\r\n'
    ser.write(data.encode())
    serial_available = True
except serial.SerialException as e:
    print(f"Warning: Could not open serial port: {e}")
    print("Running in camera-only mode (no pan-tilt control)")
    serial_available = False        

# Use camera with index 0
cap = cv2.VideoCapture(0)
print("Camera opened successfully")

while(cap.isOpened()):
    _, frame = cap.read()
    
    X, Y = Detection(frame) #执行多人脸形心检测函数
    
    if(X<10000):
        # Only send serial data if serial port is available
        if serial_available:
            #按照协议将形心坐标打包并发送至串口
            data = '#'+str(X)+'$'+str(Y)+'\r\n'
            try:
                ser.write(data.encode())
            except serial.SerialException as e:
                print(f"Error writing to serial port: {e}")
        else:
            print("Serial not available - coordinates not sent")
    
    k = cv2.waitKey(5) & 0xFF
    if k==27:   #按“Esc”退出
        break

if serial_available:
    ser.close()                                     # 关闭串口
cv2.destroyAllWindows()
cap.release()
