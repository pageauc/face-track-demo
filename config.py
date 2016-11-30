# Config.py file for face-track.py ver 0.62

# Display Settings
debug = True        # Set to False for no data display
verbose = False     # Add extra detailed information 
show_fps = True     # show frames per second processing speed
window_on = True    # Set to True displays opencv windows (GUI desktop reqd)
diff_window_on = False  # Show OpenCV image difference window
thresh_window_on = False  # Show OpenCV image Threshold window
CIRCLE_SIZE = 8     # diameter of circle to show motion location in window
LINE_THICKNESS = 2  # thickness of bounding line in pixels
WINDOW_BIGGER = 1   # Resize multiplier for OpenCV Status Window
                    # if window_on=True then makes opencv window bigger
                    # Note if the window is larger than 1 then a reduced frame rate will occur            

# Camera Settings
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240     
CAMERA_HFLIP = False
CAMERA_VFLIP = True
CAMERA_ROTATION= 0
CAMERA_FRAMERATE = 35

# FPS counter
FRAME_COUNTER = 1000  # Used for display of FPS (frames/second)

# Pan Tilt Settings
pan_servo_delay = 0.1
pan_start_x = 90   # Initial x start postion
pan_start_y = 130  # initial y start position

# Bounds checking for pan/tilt Movements.
pan_max_left = 1
pan_max_right = 179
pan_max_top = 20
pan_max_bottom = 160
pan_move_x = int(CAMERA_WIDTH / 7)  # Amount to pan left/right in search mode
pan_move_y = int(CAMERA_HEIGHT / 7) # Amount to pan up/down in search mode

timer_motion = 3      # seconds delay after no motion before looking for face
timer_face = 3        # seconds delay after no face found before starting pan search
timer_pan = 2         # seconds delay between pan seach repositioning movements

# OpenCV haarcascade Settings
fface1_haar_path = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'  # default face frontal detection
fface2_haar_path = '/usr/share/opencv/haarcascades/haarcascade_frontalface_alt2.xml'  # frontal face pattern detection
pface1_haar_path = '/usr/share/opencv/haarcascades/haarcascade_profileface.xml'		 # side face pattern detection

# OpenCV Motion Tracking Settings
MIN_AREA = 1000       # sq pixels - exclude all motion contours less than or equal to this Area
THRESHOLD_SENSITIVITY = 25
BLUR_SIZE = 10
