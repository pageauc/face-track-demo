# Config.py file for face-track.py

# Display Settings
debug = True        # Set to False for no data display
verbose = False     # Add extra detailed information 
window_on = True    # Set to True displays opencv windows (GUI desktop reqd)
diff_window_on = False  # Show OpenCV image difference window
thresh_window_on = False  # Show OpenCV image Threshold window
CIRCLE_SIZE = 8     # diameter of circle to show motion location in window
LINE_THICKNESS = 2  # thickness of bounding line in pixels
WINDOW_BIGGER = 2   # Resize multiplier for OpenCV Status Window
                    # if window_on=True then makes opencv window bigger
                    # Note if the window is larger than 1 then a reduced frame rate will occur            

# Camera Settings
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240     
CAMERA_HFLIP = False
CAMERA_VFLIP = True
CAMERA_ROTATION=0
CAMERA_FRAMERATE = 35
FRAME_COUNTER = 1000

# Pan Tilt Settings
pan_servo_delay = 0.1
pan_x_start = 100  # Initial x start postion
pan_y_start = 130  # initial y start position
# pan_start = (100, 130) # x y start position of camera pan/tilt
pan_move_x = 50
pan_move_y = 30
# bounds checking for pan/tilt search.
pan_y_bottom = 160
pan_y_top = 50
pan_y_level = 130
pan_x_left = 30
pan_x_right = 170

inactivity_timer = 3  # seconds to Wait before pan/tilt search
inactivity_cnt = 15   # Number of loops to wait between pan/tilt movement

# Timer seconds to wait before starting pan/tilt search for face.
pan_search_delay = 15

# OpenCV Settings
face_haar_path = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
face_timer = 5  # Seconds to stay in face detect mode even if there is motion.
face_retries = 15    #
face_conv = 7.0      # factor to convert face size to distance in inches

# OpenCV Motion Tracking Settings
MIN_AREA = 1000       # excludes all contours less than or equal to this Area
THRESHOLD_SENSITIVITY = 25
BLUR_SIZE = 10
