#!/usr/bin/env python
progname = "face_track.py"
ver = "version 0.55"

"""
motion-track ver 0.50 is written by Claude Pageau pageauc@gmail.com
Raspberry (Pi) - python opencv2 motion and face tracking using picamera module
attached to an openelectrons pan/tilt assembly http://www.mindsensors.com/rpi/33-pi-pan

For more details see github repo https://github.com/pageauc/face-track-demo

This is a raspberry pi python opencv2 motion and face tracking demonstration program.
It will detect motion or face in the field of view and use opencv to calculate the
largest contour or position of face and return its x,y coordinate.
It will then track using pan/tilt to keep the object/face in view. 
Some of this code is base on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Here is a my YouTube video demonstrating a similar motion tracking only
program using a Raspberry Pi B2 https://youtu.be/09JS7twPBsQ.  face-track 
is based on the motion-track code

Requires a Raspberry Pi with a RPI camera module installed and configured
. Cut and paste command below into a terminal sesssion to
download and install face_track demo.  Program will be installed to
~/face-track-demo folder and pan/tilt support files in ~/pi-pan.

curl -L https://raw.github.com/pageauc/face-track-demo/master/face-track-install.sh | bash

To Run Demo (Note a reboot may be required depending on the number of updates.

cd ~/face-track-demo
./face-track.py

"""
print("%s %s using python2 and OpenCV2" % (progname, ver))
print("Loading Please Wait ....")

import os
mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)

# Read Configuration variables from config.py file
configFilePath = baseDir + "config.py"
if not os.path.exists(configFilePath):
    print("ERROR - Missing config.py file - Could not find Configuration file %s" % (configFilePath))
    import urllib2
    config_url = "https://raw.github.com/pageauc/motion-track/master/config.py"
    print("   Attempting to Download config.py file from %s" % ( config_url ))
    try:
        wgetfile = urllib2.urlopen(config_url)
    except:
        print("ERROR - Download of config.py Failed")
        print("   Try Rerunning the face-track-install.sh Again.")
        print("   or")
        print("   Perform GitHub curl install per Readme.md")
        print("   and Try Again")
        print("Exiting %s" % ( progName ))
        quit()
    f = open('config.py','wb')
    f.write(wgetfile.read())
    f.close() 
from config import *

# import the necessary python libraries
import io
import time
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import pipan
p = pipan.PiPan()  # Initialize pipan driver   

# Create Calculated Variables
cam_cx = CAMERA_WIDTH / 2
cam_cy = CAMERA_HEIGHT / 2
big_w = int(CAMERA_WIDTH * WINDOW_BIGGER)
big_h = int(CAMERA_HEIGHT * WINDOW_BIGGER)

# Color data for OpenCV Markings
blue = (255,0,0)
green = (0,255,0)
red = (0,0,255)

#-------------------------------------------------------------------------------------------  
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------------------  
def show_FPS(start_time,frame_count):
    if debug:
        if frame_count >= FRAME_COUNTER:
            duration = float(time.time() - start_time)
            FPS = float(frame_count / duration)
            print("show_FPS - Processing at %.2f fps last %i frames" %( FPS, frame_count))
            frame_count = 0
            start_time = time.time()
        else:
            frame_count += 1
    return start_time, frame_count

#-----------------------------------------------------------------------------------------------      
def pan_goto(x, y):    # Move the pan/tilt to a specific location.
    if x <  pan_x_left:
        x = pan_x_left
    elif x > pan_x_right:
        x = pan_x_right
    elif y < pan_y_top:
        y = pan_y_top
    elif y > pan_y_bottom:
        y = pan_y_bottom
    p.do_pan(int(x))
    p.do_tilt(int(y))
    if verbose:
        print("pan_goto - moved camera to pan_cx=%3i pan_cy=%3i" % ( x, y))
    time.sleep(pan_servo_delay)
    return x, y    
    
#-----------------------------------------------------------------------------------------------  
def face_track():
    print("Initializing Camera ....") 
    # Setup video stream on a processor Thread for faster speed
    vs = PiVideoStream().start()   # Initialize video stream
    vs.camera.rotation = CAMERA_ROTATION
    vs.camera.hflip = CAMERA_HFLIP
    vs.camera.vflip = CAMERA_VFLIP
    time.sleep(2.0)    # Let camera warm up
    
    if window_on:
        print("press q to quit opencv display")
    else:
        print("press ctrl-c to quit")        
    cx, cy, cw, ch = 0, 0, 0, 0
    mx, my, mw, mh = 0, 0, 0, 0
    fx, fy, fw, fh = 0, 0, 0, 0  
    pan_cx = cam_cx
    pan_cy = cam_cy    
    frame_count = 0
    inactivity_start = time.time()
    loop_cnt = 0
    start_time = time.time()
    face_cascade = cv2.CascadeClassifier(face_haar_path)   
    still_scanning = True
    pan_cx, pan_cy = pan_goto(pan_x_start, pan_y_start)   # Position Pan/Tilt to start position
    image2 = vs.read()     
    image1 = image2
    grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)    
    face_cnt = 0
    print("Start Tracking Motion and Faces ....")    
    while still_scanning:
        motion_found = False
        face_found = False                    
        Nav_LR = 0
        Nav_UD = 0                
        start_time, frame_count = show_FPS(start_time, frame_count)    
        image2 = vs.read()        
        grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        if face_cnt < 1:          
            # Search for Motion and Track
            # Get differences between the two greyed, blurred images    
            differenceimage = cv2.absdiff(grayimage1, grayimage2)
            differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
            # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
            retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)
            # Get all the contours found in the thresholdimage
            contours, hierarchy = cv2.findContours(thresholdimage,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            total_contours = len(contours)
            # save grayimage2 to grayimage1 ready for next image2
            grayimage1 = grayimage2
            # find contour with biggest area
            biggest_area = MIN_AREA            
            for c in contours:
                # get area of next contour
                found_area = cv2.contourArea(c)
                # find the middle of largest bounding rectangle           
                if found_area > biggest_area:
                    motion_found = True
                    biggest_area = found_area
                    (x, y, w, h) = cv2.boundingRect(c)
                    mx = x
                    my = y
                    mw = w
                    mh = h

            if motion_found:
                cx = mx + mw/2   
                cy = my + mh/2   
                if debug:
                    print("face-track - Motion At cx=%3i cy=%3i  total_Contours=%2i  biggest_area:%3ix%3i=%5i" % (cx ,cy, total_contours, mw, mh, biggest_area))
                Nav_LR = int((cam_cx - cx) / 7)
                Nav_UD = int((cam_cy - cy) / 6)
                pan_cx = pan_cx - Nav_LR 
                pan_cy = pan_cy - Nav_UD
                if debug:            
                    print("face-track - Pan To pan_cx=%3i pan_cy=%3i Nav_LR=%3i Nav_UD=%3i " % (pan_cx, pan_cy, Nav_LR, Nav_UD))                
                # pan_goto(pan_cx, pan_cy)
                pan_cx, pan_cy = pan_goto(pan_cx, pan_cy)
                inactivity_start = time.time()                 
            elif time.time() - inactivity_start > inactivity_timer:
                loop_cnt += 1  
                if loop_cnt > inactivity_cnt: # give camera a few cycles to find a face or motion.
                    loop_cnt = 0
                else:
                    pan_cx = pan_cx + pan_move_x
                    if pan_cx > pan_x_right:
                        pan_cx = pan_x_left         
                        pan_cy = pan_cy + pan_move_y
                        if pan_cy > pan_y_top:
                            pan_cy = pan_y_bottom     
                    if debug:
                        print("face_track - Reposition Pan/Tilt loop_cnt=%i Inactivity_timer=%i  > %.1f seconds" % (loop_cnt, inactivity_timer, time.time() - inactivity_start))
                    pan_cx, pan_cy = pan_goto (pan_cx, pan_cy)
            else:
                face_cnt += 1     
        else:
            # Search for Face if no motion detected 
            if verbose:
                print("face-track - Searching for Face ... ")
            biggest_face = 0                
            faces = face_cascade.detectMultiScale(grayimage2, 1.2, 1)
            for (x, y, w, h) in faces:
                if h > biggest_face:        
                    face_found = True
                    fx = x
                    fy = y
                    fw = w
                    fh = h                     
                    biggest_face = fh    
 
            if face_found:
                face_cnt = 1
                cx = fx + fw/2   
                cy = fy + fh/2                 
                Nav_LR = int((cam_cx - cx) /7 )
                Nav_UD = int((cam_cy - cy) /6 )
                pan_cx = pan_cx - Nav_LR 
                pan_cy = pan_cy - Nav_UD
                if debug:            
                    print("face-track - Found Face at pan_cx=%3i pan_cy=%3i Nav_LR=%3i Nav_UD=%3i "
                                                     % (pan_cx, pan_cy, Nav_LR, Nav_UD))                    
                pan_cx, pan_cy = pan_goto(pan_cx, pan_cy)
                inactivity_start = time.time()                  
            else:
                face_cnt += 1  # increment face counter             
                if face_cnt > face_retries:
                    face_cnt = 0                                            
                
        if window_on:
            if diff_window_on:
                cv2.imshow('Difference Image',differenceimage) 
            if thresh_window_on:
                cv2.imshow('OpenCV Threshold', thresholdimage)        
            if face_found:            
                cv2.rectangle(image2,(fx,fy), (fx+fw,fy+fh), blue, LINE_THICKNESS)
            if motion_found:
                cv2.circle(image2, (cx,cy), CIRCLE_SIZE, green, LINE_THICKNESS)
                
            if WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
                image2 = cv2.resize( image2,( big_w, big_h ))                     
            cv2.imshow('Track (Press q in Window to Quit)', image2)
            
            # Close Window if q pressed while movement status window selected
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                vs.stop()
                print("face_track - End Motion Tracking")
                still_scanning = False

#-----------------------------------------------------------------------------------------------    
if __name__ == '__main__':
    try:
        face_track()
    finally:
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("%s %s - Exiting" % (progname, ver))
        print("+++++++++++++++++++++++++++++++++++")
        print("")                                



