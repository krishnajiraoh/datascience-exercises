import cv2
import argparse
import numpy as np
from imutils.video import VideoStream
import time
import imutils

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
writer = None

#print(args.video)
vs = cv2.VideoCapture("Video_Trim.mp4")

frame_width = int(vs.get(3)) 
frame_height = int(vs.get(4)) 
   
#frame_width = 400
size = (frame_width, frame_height) 

print(size)

fourcc = cv2.VideoWriter_fourcc(*"MJPG")
#fourcc = cv2.VideoWriter_fourcc(*'XVID')

#writer = cv2.VideoWriter("output/infer.avi", fourcc , 30, size, True)
writer = cv2.VideoWriter("timelapseTrim.mp4", 0x7634706d , 30, size, True)

count = 0

while vs.isOpened():
    ret, frame = vs.read()

    if ret:
        #cv2.imwrite('frame{:d}.jpg'.format(count), frame)
        count += 30 # i.e. at 30 fps, this advances one second
        vs.set(1, count)
    else:
        vs.release()
        break

    
    # if the video writer is not None, write the frame to the output
    # video file
    if writer is not None:
        #print(frame.shape)
        writer.write(frame)
        
    #print(frame.shape)
    cv2.waitKey(500)
    
print('output file is ready')
cv2.destroyAllWindows()