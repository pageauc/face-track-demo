#!/usr/bin/env python
progname = "face_track.py"
ver = "ver 0.62"

"""
motion-track is written by Claude Pageau pageauc@gmail.com
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
print("===================================")
print("%s %s using python2 and OpenCV2" % (progname, ver))
print("Loading Libraries  Please Wait ....")

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
    config_url = "https://raw.github.com/pageauc/face-track-demo/master/config.py"
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

# Setup haar_cascade variables
face_cascade = cv2.CascadeClassifier(fface1_haar_path) 
frontalface = cv2.CascadeClassifier(fface2_haar_path) 
profileface = cv2.CascadeClassifier(pface1_haar_path) 

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
def show_FPS(start_time, fps_count):
    if debug:
        if fps_count >= FRAME_COUNTER:
            duration = float(time.time() - start_time)
            FPS = float(fps_count / duration)
            print("show_FPS - Processing at %.2f fps last %i frames" %( FPS, fps_count))
            fps_count = 0
            start_time = time.time()
        else:
            fps_count += 1
    return start_time, fps_count

#-----------------------------------------------------------------------------------------------          
def check_timer(start_time, duration):
    if time.time() - start_time > duration:
       stop_timer = False
    else:
       stop_timer = True
    return stop_timer
 
#-----------------------------------------------------------------------------------------------      
def pan_goto(x, y):    # Move the pan/tilt to a specific location.
    if x <  pan_max_left:
        x = pan_max_left
    elif x > pan_max_right:
        x = pan_max_right
    p.do_pan(int(x))
    time.sleep(pan_servo_delay)  # give the servo's some time to move          
    if y < pan_max_top:
        y = pan_max_top
    elif y > pan_max_bottom:
        y = pan_max_bottom 
    p.do_tilt(int(y))
    time.sleep(pan_servo_delay)  # give the servo's some time to move    
    if verbose:
        print("pan_goto - Moved Camera to pan_cx=%i pan_cy=%i" % ( x, y ))
    return x, y    

#-----------------------------------------------------------------------------------------------
def pan_search(pan_cx, pan_cy):
    pan_cx = pan_cx + pan_move_x
    if pan_cx > pan_max_right:
        pan_cx = pan_max_left         
        pan_cy = pan_cy + pan_move_y
        if pan_cy > pan_max_bottom:
            pan_cy = pan_max_top     
    if debug:            
        print("pan_search - at pan_cx=%i pan_cy=%i "
                            % (pan_cx, pan_cy))        
    return pan_cx, pan_cy

#-----------------------------------------------------------------------------------------------    
def motion_detect(gray_img_1, gray_img_2):
    motion_found = False
    biggest_area = MIN_AREA      
    # Process images to see if there is motion    
    differenceimage = cv2.absdiff(gray_img_1, gray_img_2)
    differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
    # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
    retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)
    # Get all the contours found in the thresholdimage
    contours, hierarchy = cv2.findContours(thresholdimage,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if contours != ():    # Check if Motion Found
        for c in contours:   
            found_area = cv2.contourArea(c) # Get area of current contour   
            if found_area > biggest_area:   # Check if it has the biggest area
                biggest_area = found_area   # If bigger then update biggest_area            
                (mx, my, mw, mh) = cv2.boundingRect(c)    # get motion contour data       
                motion_found = True
        if motion_found:    
            motion_center = (int(mx + mw/2), int(my + mh/2))
            if verbose:
                print("motion-detect - Found Motion at px cx,cy (%i, %i) Area w%i x h%i = %i sq px" % (int(mx + mw/2), int(my + mh/2), mw, mh, biggest_area))
        else:
            motion_center = ()
    else:
        motion_center = ()
    return motion_center
 
#-----------------------------------------------------------------------------------------------
def face_detect(image):
    # Look for Frontal Face
    ffaces = face_cascade.detectMultiScale(image, 1.2, 1)    
    if ffaces != ():
        for f in ffaces:
            face = f
        if verbose:
            print("face_detect - Found Frontal Face using face_cascade")            
    else:
        # Look for Profile Face if Frontal Face Not Found
        pfaces = profileface.detectMultiScale(image, 1.2, 1)  # This seems to work better than below           
        # pfaces = profileface.detectMultiScale(image,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING 
        #                                                   + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT
        #                                                   + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(80,80)) 
        if pfaces != ():			# Check if Profile Face Found
            for f in pfaces:		# f in pface is an array with a rectangle representing a face
                face = f
            if verbose:
                print("face_detect - Found Profile Face using profileface")          
 
        else:
            ffaces = frontalface.detectMultiScale(image, 1.2, 1)  # This seems to work better than below
            #ffaces = frontalface.detectMultiScale(image,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING 
            #                                                  + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT 
            #                                                  + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(60,60))    
            if ffaces != ():			# Check if Frontal Face Found
                for f in ffaces:		# f in fface is an array with a rectangle representing a face
                    face = f 
                if verbose:
                    print("face_detect - Found Frontal Face using frontalface")            
            else:
                face = ()                 
    return face
    
#-----------------------------------------------------------------------------------------------  
def face_track():
    print("Initializing Pi Camera ....") 
    if window_on:
        print("press q to quit opencv window display")
    else:
        print("press ctrl-c to quit SSH or terminal session")
        
    # Setup video stream on a processor Thread for faster speed
    vs = PiVideoStream().start()   # Initialize video stream
    vs.camera.rotation = CAMERA_ROTATION
    vs.camera.hflip = CAMERA_HFLIP
    vs.camera.vflip = CAMERA_VFLIP
    time.sleep(2.0)    # Let camera warm up   
    
    pan_cx = cam_cx
    pan_cy = cam_cy    
    fps_counter = 0
    fps_start = time.time()

    motion_start = time.time()
    face_start = time.time()
    pan_start = time.time()
    
    img_frame = vs.read()
    print("Position pan/tilt to (%i, %i)" % (pan_start_x, pan_start_y))
    pan_cx, pan_cy = pan_goto(pan_start_x, pan_start_y)   # Position Pan/Tilt to start position   
    grayimage1 = cv2.cvtColor(img_frame, cv2.COLOR_BGR2GRAY)
    print("===================================")   
    print("Start Tracking Motion and Faces....")
    print("")    
    still_scanning = True   
    while still_scanning:
        motion_found = False
        face_found = False                    
        Nav_LR = 0
        Nav_UD = 0
        if show_fps:       
            fps_start, fps_counter = show_FPS(fps_start, fps_counter)    
        img_frame = vs.read()        
        if check_timer(motion_start, timer_motion): 
            # Search for Motion and Track
            grayimage2 = cv2.cvtColor(img_frame, cv2.COLOR_BGR2GRAY)
            motion_center = motion_detect(grayimage1, grayimage2)            
            grayimage1 = grayimage2  # Reset grayimage1 for next loop
            if motion_center != ():
                motion_found = True
                cx = motion_center[0]
                cy = motion_center[1]                
                if debug:
                    print("face-track - Motion At cx=%3i cy=%3i " % (cx, cy))
                Nav_LR = int((cam_cx - cx) / 7)
                Nav_UD = int((cam_cy - cy) / 6)
                pan_cx = pan_cx - Nav_LR 
                pan_cy = pan_cy - Nav_UD
                if debug:            
                    print("face-track - Pan To pan_cx=%3i pan_cy=%3i Nav_LR=%3i Nav_UD=%3i "
                                            % (pan_cx, pan_cy, Nav_LR, Nav_UD))                
                # pan_goto(pan_cx, pan_cy)
                pan_cx, pan_cy = pan_goto(pan_cx, pan_cy)
                motion_start = time.time()
            else:                
                face_start = time.time()
        elif check_timer(face_start, timer_face):
            # Search for Face if no motion detected for a specified time period        
            face_data = face_detect(img_frame)
            if face_data != ():
                face_found = True
                (fx, fy, fw, fh) = face_data
                cx = int(fx + fw/2)
                cy = int(fy + fh/2)                     
                Nav_LR = int((cam_cx - cx) /7 )
                Nav_UD = int((cam_cy - cy) /6 )
                pan_cx = pan_cx - Nav_LR 
                pan_cy = pan_cy - Nav_UD
                if debug:            
                    print("face-track - Found Face at pan_cx=%3i pan_cy=%3i Nav_LR=%3i Nav_UD=%3i "
                                                   % (pan_cx, pan_cy, Nav_LR, Nav_UD))                    
                pan_cx, pan_cy = pan_goto(pan_cx, pan_cy)
                face_start = time.time()
            else:
                pan_start = time.time()            
        elif check_timer(pan_start, timer_pan):
            pan_cx, pan_cy = pan_search(pan_cx, pan_cy)
            pan_cx, pan_cy = pan_goto (pan_cx, pan_cy)
            img_frame = vs.read() 
            grayimage1 = cv2.cvtColor(img_frame, cv2.COLOR_BGR2GRAY)               
            pan_start = time.time()            
            motion_start = time.time()            
        else:
            motion_start = time.time()
   
        if window_on:
            if face_found:            
                cv2.rectangle(img_frame,(fx,fy), (fx+fw,fy+fh), blue, LINE_THICKNESS)
            if motion_found:
                cv2.circle(img_frame, (cx,cy), CIRCLE_SIZE, green, LINE_THICKNESS)
                
            if WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
                img_frame = cv2.resize( img_frame,( big_w, big_h ))
                
            cv2.imshow('Track (Press q in Window to Quit)', img_frame)
            
            # Close Window if q pressed while movement status window selected
            if cv2.waitKey(1) & 0xFF == ord('q'):
                vs.stop()           
                cv2.destroyAllWindows()
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



