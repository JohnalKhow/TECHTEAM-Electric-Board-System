import numpy as np
import cv2
import os
from collections import deque

#FILETYPE
filename = 'Screen_Capture.avi'
frames_per_second = 30.0
res = '480p'

# Set resolution for the video capture
# Function adapted from https://kirr.co/0l6qmh
def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

# Standard Video Dimensions Sizes
STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

# grab resolution dimensions and set video capture to it.
def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height

# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    #'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
      return  VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']

# Define the upper and lower boundaries for a color to be considered "Blue"
yellowLower = np.array([20, 100, 100])
yellowUpper = np.array([30, 255, 255])

# Define a 5x5 kernel for erosion and dilation
kernel = np.ones((5, 5), np.uint8)

# Setup deques to store separate colors in separate arrays
bpoints = [deque(maxlen=512)]
gpoints = [deque(maxlen=512)]
rpoints = [deque(maxlen=512)]
wpoints = [deque(maxlen=512)]

bindex = 0
gindex = 0
rindex = 0
windex = 0

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]
colorIndex = 0
pxIndex=2

# Load the video
camera = cv2.VideoCapture(0)
out = cv2.VideoWriter(filename, get_video_type(filename), 25, get_dims(camera, res))
# Keep looping
while True:
    # Grab the current paintWindow
    (grabbed, frame) = camera.read()
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame = cv2.rectangle(frame, (0,60), (800,110), (122,122,122), -1)
    
    #CIRCLE CHOICE BOX FOR COLORS
    cv2.circle(frame, (40,150), 25, colors[0], -1)
    cv2.circle(frame, (40,210), 25, colors[1], -1)
    cv2.circle(frame, (40,270), 25, colors[2], -1)
    cv2.circle(frame, (40,330), 25, colors[3], -1)
    
    #CIRCLE CHOICE BOX FOR PIXELS
    cv2.circle(frame, (600,150), 25, colors[3], -1)
    cv2.circle(frame, (600,210), 25, colors[3], -1)
    cv2.circle(frame, (600,270), 25, colors[3], -1)
    cv2.circle(frame, (600,330), 25, colors[3], -1)
    
    #RECTANGLE TEXT
    cv2.putText(frame, "ERASE", (280, 90), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
    #CIRCLE TEXT
    cv2.putText(frame, "1px", (585, 155), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "2px", (585, 215), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255,255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "3px", (585, 275), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "5px", (585, 335), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255,255, 255), 1, cv2.LINE_AA)
    
    
    if not grabbed:
        break


    yellowMask = cv2.inRange(hsv, yellowLower, yellowUpper)
    yellowMask = cv2.erode(yellowMask, kernel, iterations=2)
    yellowMask = cv2.morphologyEx(yellowMask, cv2.MORPH_OPEN, kernel)
    yellowMask = cv2.dilate(yellowMask, kernel, iterations=1)

    (cnts, _) = cv2.findContours(yellowMask.copy(), cv2.RETR_EXTERNAL,
    	cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:

        cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if center[1] <= 110:
            if 0 <= center[0] <= 800:
                bpoints = [deque(maxlen=512)]
                gpoints = [deque(maxlen=512)]
                rpoints = [deque(maxlen=512)]
                wpoints = [deque(maxlen=512)]

                bindex = 0
                gindex = 0
                rindex = 0
                windex = 0
             
        elif center[0] <=65:
            if 150 <= center[1] <= 180: 
                  colorIndex = 0 # Blue
            elif 210 <= center[1] <= 240: 
                  colorIndex = 1 # Green
            elif 270 <= center[1] <= 300:
                    colorIndex = 2 # Red
            elif 300 <= center[1] <= 330:
                    colorIndex = 3 # Black
                    
        elif center[0] >=585:
            if 150 <= center[1] <= 180: 
                  pxIndex = 1 # 1px
            elif 210 <= center[1] <= 240: 
                  pxIndex = 2 # 2px
            elif 270 <= center[1] <= 300:
                  pxIndex = 3 # 3px
            elif 300 <= center[1] <= 330:
                  pxIndex = 5 # 5px
                  
        else :
            if colorIndex == 0:
                bpoints[bindex].appendleft(center)
            elif colorIndex == 1:
                gpoints[gindex].appendleft(center)
            elif colorIndex == 2:
                rpoints[rindex].appendleft(center)
            elif colorIndex == 3:
                wpoints[windex].appendleft(center)
 
    else:
        bpoints.append(deque(maxlen=512))
        bindex += 1
        gpoints.append(deque(maxlen=512))
        gindex += 1
        rpoints.append(deque(maxlen=512))
        rindex += 1
        wpoints.append(deque(maxlen=512))
        windex += 1


    points = [bpoints, gpoints, rpoints, wpoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], pxIndex)

    # Show the frame and the paintWindow image
    cv2.imshow("Electronic Board System ", frame)
    out.write(frame)

    if cv2.waitKey(1) == 27:
        break

# Cleanup the camera and close any open windows
camera.release()
out.release()
cv2.destroyAllWindows()
