#!/bin/bash
# face-track-install-gpiozero.sh script written by Claude Pageau 24-Nov-2016
ver="0.5"
APP_DIR='face-track-demo'  # Default folder install location

cd ~
if [ -d "$APP_DIR" ] ; then
  STATUS="Upgrade"
  echo "Upgrade face-track files"
else  
  echo "New face-track Install"
  STATUS="New Install"
  mkdir -p $APP_DIR
  echo "$APP_DIR Folder Created"
fi 

cd $APP_DIR
INSTALL_PATH=$( pwd )   

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "------------------------------------------------"
echo "  face-track-Install-gpiozero.sh script ver $ver"
echo "  $STATUS face-track for python gpiozero setup"
echo "  Face and Motion Tracking Pan/Tilt Camera Demo"
echo "------------------------------------------------"
echo ""
echo "1 - Downloading GitHub Repo files to $INSTALL_PATH"
wget -O face-track-install-gpiozero.sh -q --show-progress https://raw.github.com/pageauc/face-track-demo/master/face-track-install-gpiozero.sh
if [ $? -ne 0 ] ;  then
  wget -O face-track-install-gpiozero.sh https://raw.github.com/pageauc/face-track-demo/master/face-track-install-gpiozero.sh
  wget -O face-track-gpiozero.py https://raw.github.com/pageauc/face-track-demo/master/face-track-gpiozero.py 
  wget -O config.py https://raw.github.com/pageauc/face-track-demo/master/config.py  
  wget -O Readme.md https://raw.github.com/pageauc/face-track-demo/master/Readme.md  
else
  wget -O face-track-gpiozero.py -q --show-progress https://raw.github.com/pageauc/face-track-demo/master/face-track-gpiozero.py
  wget -O config.py -q --show-progress https://raw.github.com/pageauc/face-track-demo/master/config.py    
  wget -O Readme.md -q --show-progress  https://raw.github.com/pageauc/face-track-demo/master/Readme.md  
fi
echo "Done Download of Github Files"
echo "------------------------------------------------"
echo ""
echo "2 - Make required Files Executable"
chmod +x face-track-gpiozero.py
chmod +x face-track-install-gpiozero.sh
echo "Done Permissions"
echo "------------------------------------------------"
echo ""
# check if system was updated today
NOW="$( date +%d-%m-%y )"
LAST="$( date -r /var/lib/dpkg/info +%d-%m-%y )"
if [ "$NOW" == "$LAST" ] ; then
  echo "1 Raspbian System is Up To Date"
  echo ""  
else
  echo ""
  echo "4 - Performing Raspbian System Update"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y update
  echo "Done update"
  echo "------------------------------------------------"
  echo ""
  echo "2 - Performing Raspbian System Upgrade"
  echo "     This Will Take Some Time ...."
  echo ""
  sudo apt-get -y upgrade
  echo "Done upgrade"
fi  
echo "------------------------------------------------"
echo ""
echo "3 - Installing OpenCV and python-picamera Libraries"
sudo apt-get install -y python-picamera python-imaging python-pyexiv2 libgl1-mesa-dri
sudo apt-get install -y python-gpiozero
sudo apt-get install -y libopencv-dev python-opencv
sudo apt-get install -y fonts-freefont-ttf # Required for Jessie Lite Only
echo ""
echo "Install Dependencies Complete"
echo "-----------------------------------------------"
echo "4 - $STATUS Complete"
echo "-----------------------------------------------"
echo ""
echo "1. Reboot RPI if there are significant Raspbian system updates"
echo "2. Raspberry pi needs a monitor/TV attached to display OpenCV window"
echo "3. Default gpiozero pins are 17 and 23 per variables"
echo "4. Run face-track-gpiozero.py with the Raspbian Desktop GUI running"
echo "5. To start open file manager or a Terminal session then change to" 
echo "   face-track-demo folder and launch per commands below"
echo "6. IMPORTANT You MUST have gpiozero configured for your camera"
echo "             pan-tilt servo setup. Default pan_pin=17 and tilt_pin=23"
echo "7. A RPI-3 or Quad core RPI is recommended due to video stream threading"
echo "8. Edit the config.py file to tune variables as needed"
echo ""
echo "   cd ~/face-track-demo"
echo "   ./face-track-gpiozero.py"
echo ""
echo "-----------------------------------------------"
echo "See Readme.md for Further Details"
echo $APP_DIR "Good Luck Claude ..."
echo "Bye"
echo ""