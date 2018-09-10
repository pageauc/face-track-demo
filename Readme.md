## Raspberry Pi Camera Pan/Tilt Face and Motion Tracking Demo
#### Uses python & Opencv to Track x,y position of moving object/face in camera view  

Can use openelectrons pan/tilt assembly per http://www.mindsensors.com/rpi/33-pi-pan     
or   
gpiozero and pan/tilt servos connected to appropriate RPI gpio pins
per https://github.com/RPi-Distro/python-gpiozero

### Quick Install   
Easy Install of face-track-demo onto a Raspberry Pi Computer with latest Raspbian Stretch (recommended). 

***for pi-pan openelectrons controller***   

    curl -L https://raw.github.com/pageauc/face-track-demo/master/face-track-install-pipan.sh | bash

***for gpiozero servo control***
    
    curl -L https://raw.github.com/pageauc/face-track-demo/master/face-track-install-gpiozero.sh | bash    
    
From a computer logged into the RPI via ssh(Putty) session use mouse to highlight appropriate command above, right click, copy.  
Then select ssh(Putty) window, mouse right click, paste.  The command should 
download and execute the github script and install the face-track-demo project.  
This install can also be done directly on an Internet connected Raspberry Pi
via SSH (Putty), console or gui desktop terminal session and web a browser if you wish to copy the link.       
Note - a Raspbian sudo apt-get update and upgrade will be performed as part of install 
so it may take some time if these are not up-to-date.

### Manual Install   
From logged in RPI SSH session or console terminal perform the following.

***for pi-pan openelectrons controller***  

    wget https://raw.github.com/pageauc/face-track-demo/master/face-track-install-pipan.sh
    chmod +x face-track-install-pipan.sh
    ./face-track-install-pipan.sh
   
***for gpiozero servo control***  
 
    wget https://raw.github.com/pageauc/face-track-demo/master/face-track-install-gpiozero.sh
    chmod +x face-track-install-gpiozero.sh
    ./face-track-install-gpiozero.sh
    
### How to Run

#### OpenElectrons
The face-track-install.sh program will require an openelectrons pan/tilt assembly and servo controller installed
and tested see http://www.mindsensors.com/rpi/33-pi-pan. See web site for installation details. 
This program installs and uses servo blaster and the pipan python
library.  See the face-track-install-pipan.sh for details.  Support programs and utilities are installed
in the /home/pi/pi-pan folder.  These can be used to test the openelectrons pan/tilt operation.
From SSH session, console or GUI desktop terminal session execute the following commands 

    cd ~/face-track-demo
    ./face-track-pipan.py   

#### gpiozero
The face-track-install-gpiozero.sh will require pan/tilt servos connected to the appropriate RPI gpio pins per 
details and documentation links at https://github.com/RPi-Distro/python-gpiozero
From SSH session, console or GUI desktop terminal session execute the following commands 

    cd ~/face-track-demo
    ./face-track-gpiozero.py   

#### GUI or SSH display
Default is Jessie GUI desktop display. Use Nano to Edit config.py variables. 
default is window_on=True to display the opencv tracking window on GUI desktop.   
See other variables and descriptions for additional variable customization settings.

The program can be run headless if required by setting config.py variable window_on=False 
  
### Face and Motion Track Demo - Basic concept of tracking moving objects
This Demo program detects motion and/or faces in the field of view and uses opencv to calculate the 
largest contour above a minimum size and return its x,y coordinate.  The object is then tracked using
the camera pan/tilt (within the range of motion available) 
* Motion Track Demo YouTube Video http://youtu.be/09JS7twPBsQ  
* GitHub Repo https://github.com/pageauc/face-track-demo

### Introduction
I did quite a bit of searching on the internet, github, etc, but could not
at the time find a similar python picamera implementation that returns x,y coordinates of
the most dominate moving object in the frame although some came close. I have added face tracking.

* If motion is detected then the largest moving contour will be tracked and a circle will
indicate the center of the opencv contour   
* If no motion is detected for a while then face detection will be started.   
* If a face is found then it will be tracked and a rectangle will highlight the face contour.   
* If a face cannot be found after a specified number of retries then detection will
revert back to looking for motion.   
* If there there is no face or motion detected for a longer delay then
the camera will pan and tilt to look around until motion or a face is detected.   

This setup may need to be tuned for your needs using the variables in the config.py file.
I have tested this on a RPI 3 (quad core) and RPI B (single core). Performance on the RPI3 is reasonable although pretty
laggy on the single core RPI B. Face detection takes a bit longer than regular opencv motion detection.   
You may want to change the cascade file path to test other body parts per cascade files.     
These can be found in the folder

    /usr/share/opencv/haarcascades

Change the config.py file face_haar_path variable.    
    
### Prerequisites
IMPORTANT - You must have the RPI connected to a network with internet access during the installation.  No
internet connection is required otherwise.       
For best results use a Quad core Raspberry Pi computer (recommended). You must be running with an up-to-date raspbian jessie distro and a
RPI camera module installed on an OpenElectrons Pan/Tilt assembly that has been installed, configured and tested.
Required python and servoblaster files and library Dependencies will be 
installed/upgraded per face-track-install.sh script depending on your previous installs.  Note a sudo apt-get update and upgrade
will be performed as part of the automated install so it may take some time depending on how up-to-date your system is. 

### Disable Camera LED

To disable the red LED you simply need to add the following line to your config.txt file :

    disable_camera_led=1
    
To edit the config.txt file you can use Nano :

    sudo nano /boot/config.txt

### Trouble Shooting
    
if you get an opengl error first check that you are running the Desktop. If there is still a problem
then see this article about installing opengl on 
a RPI P2  https://www.raspberrypi.org/blog/another-new-raspbian-release/

Otherwise install opengl support library per following command then reboot.

    sudo apt-get install libgl1-mesa-dri
    
Edit the config.py file and set variable window_on = True so the opencv status windows can display camera
motion images and a motion circle or face rectangle marking x,y coordinates as well as
the threshold images.  The circle diameter can be change using CIRCLE_SIZE
variable.  
You can set window_on = False if you need to run from SSH session.  If debug=True
then status information will be displayed without a GUI desktop session.

### Credits  
Some of this code is based on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Thanks to Adrian Rosebrock jrosebr1 at http://www.pyimagesearch.com 
for the PiVideoStream Class code available on github at
https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py

 
## ---------- Other Raspberry Pi Projects Based on Motion Tracking ------------

### speed-camera.py - Object (vehicle) speed camera based on motion tracking
Tracks vehicle speeds or other moving objects in real time and records image 
and logs data. Now improved using threading for video stream and clipping of 
area of interest for greater performance.  
* GitHub Repo https://github.com/pageauc/rpi-speed-camera
* YouTube Speed Camera Video https://youtu.be/eRi50BbJUro  
* RPI forum post https://www.raspberrypi.org/forums/viewtopic.php?p=1004150#p1004150  

### cam-track.py - Tracks camera x y movements
Uses a clipped search image rectangle to search subsequent video stream images and returns
the location. Can be used for tracking camera x y movements for stabilization,
robotics, Etc.  
* GitHub Repo https://github.com/pageauc/rpi-cam-track
* YouTube Cam-Track Video https://www.youtube.com/edit?video_id=yjA3UtwbD80   
* Code Walkthrough YouTube Video https://youtu.be/lkh3YbbNdYg        
* RPI Forum Post https://www.raspberrypi.org/forums/viewtopic.php?p=1027463#p1027463   

### hotspot-game.py - A simple motion tracking game
The game play involves using streaming video of body motion to get as many hits 
as possible inside shrinking boxes that randomly move around the screen. 
Position the camera so you can see body motions either close or standing. 
Pretty simple but I think kids would have fun with it and they just might 
take a look at the code to see how it works, change variables or game logic.      
* GitHub hotspot-game Repo https://github.com/pageauc/hotspot-game 
* YouTube Hotspot Gam Video https://youtu.be/xFl3lmbEO9Y       
* RPI Forum Post https://www.raspberrypi.org/forums/viewtopic.php?p=1026124#p1026124   

## ----------------------------------------------------------------------------
 
Have Fun   
Claude Pageau    
YouTube Channel https://www.youtube.com/user/pageaucp   
GitHub Repo https://github.com/pageauc

