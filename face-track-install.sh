#!/bin/bash
# face-track-install.sh script written by Claude Pageau 24-Nov-2016
ver="1.2"
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
echo "  face-track-Install.sh script ver $ver"
echo "  $STATUS face-track for OpenElectrons Pan/Tilt"
echo "  Face and Motion Tracking Pan/Tilt Camera Demo"
echo "------------------------------------------------"
echo ""
echo "1 - Downloading GitHub Repo files to $INSTALL_PATH"
wget -O face-track-install.sh -q --show-progress https://raw.github.com/pageauc/face-track-demo/master/face-track-install.sh
if [ $? -ne 0 ] ;  then
  wget -O face-track-install.sh https://raw.github.com/pageauc/face-track-demo/master/face-track-install.sh
  wget -O face-track.py https://raw.github.com/pageauc/face-track-demo/master/face-track.py 
  wget -O config.py https://raw.github.com/pageauc/face-track-demo/master/config.py  
  wget -O Readme.md https://raw.github.com/pageauc/face-track-demo/master/Readme.md  
else
  wget -O face-track.py -q --show-progress https://raw.github.com/pageauc/face-track-demo/master/face-track.py
  wget -O config.py -q --show-progress https://raw.github.com/pageauc/face-track-demo/master/config.py    
  wget -O Readme.md -q --show-progress  https://raw.github.com/pageauc/face-track-demo/master/Readme.md  
fi
echo "Done Download"
echo "------------------------------------------------"
echo ""
echo "2 - Make required Files Executable"
chmod +x face-track.py
chmod +x face-track-install.sh
echo "Done Permissions"
echo "------------------------------------------------"
echo ""
echo "3 - Install pi-pan files to /home/pi/pi-pan"
cd ~
rm pi-pan-2016-Jessie.tar.gz 
echo "Downloading http://www.mindsensors.com/largefiles/pi-pan-2016-Jessie.tar.gz"
wget http://www.mindsensors.com/largefiles/pi-pan-2016-Jessie.tar.gz
echo "Extracting files to /home/pi/pi-pan folder"
tar -zxvf pi-pan-2016-Jessie.tar.gz
echo "Download and Install pi-pan python library"
sudo apt-get install python-setuptools -y
sudo easy_install pip
sudo pip install pipan
cd ~/pi-pan
# Check if servod file exists and install
if [ -e  servod ]
then
    if [ -e /etc/init.d/servoblaster.sh ]
    then
        sudo /etc/init.d/servoblaster.sh stop > /dev/null
    fi
    sudo cp servod /usr/local/sbin
else
    echo "ERROR - missing servod. Possible cause bad download."
    exit 1
fi
# Check if servoblaster exist and install as service
if [ -e  servoblaster.sh ]
then
    echo "Installing servoblaster"
    sudo cp servoblaster.sh /etc/init.d
    # Activate servoblaster service on startup
    sudo update-rc.d servoblaster.sh defaults 92 08
    echo "start servoblaster service" 
    sudo /etc/init.d/servoblaster.sh start > /dev/null
    echo "servoblaster install complete"    
else
    echo "ERROR - Missing servoblaster.sh Possible cause bad download"
    exit 1
fi
echo "Done pi-pan and servoblaster install"
echo "------------------------------------------------"
echo ""
# check if system was updated today
NOW="$( date +%d-%m-%y )"
LAST="$( date -r /var/lib/dpkg/info +%d-%m-%y )"
if [ "$NOW" == "$LAST" ] ; then
  echo "4 Raspbian System is Up To Date"
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
  echo "5 - Performing Raspbian System Upgrade"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y upgrade
  echo "Done upgrade"
fi  
echo "------------------------------------------------"
echo ""
echo "6 - Installing OpenCV and python-picamera Libraries"
sudo apt-get install -y python-picamera python-imaging python-pyexiv2 libgl1-mesa-dri
sudo apt-get install -y libopencv-dev python-opencv
sudo apt-get install -y fonts-freefont-ttf # Required for Jessie Lite Only
echo ""
echo "Install Dependencies Complete"
echo "------------------------------------------------"
echo ""
echo "Please test camera pan/tilt using pi-pan utilities"
echo "Then test the camera operation using raspistill"
cd $DIR
# Check if face-track-install.sh was launched from face-track-demo folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -e 'face-track-install.sh' ]; then
    echo "$STATUS Cleanup face-track-install.sh"
    rm face-track-install.sh
  fi
fi
rm ~/pi-pan-2016-Jessie.tar.gz  
echo "-----------------------------------------------"
echo "6 - $STATUS Complete"
echo "-----------------------------------------------"
echo ""
echo "1. Reboot RPI if there are significant Raspbian system updates"
echo "2. Raspberry pi needs a monitor/TV attached to display OpenCV window"
echo "3. Run face-track.py with the Raspbian Desktop GUI running"
echo "4. To start open file manager or a Terminal session then change to" 
echo "   face-track-demo folder and launch per commands below"
echo "5. IMPORTANT You MUST have an OpenElectrons or compatible pan/tilt controller"
echo "             and pan-tilt camera servo mechanism attached and tested"
echo "6. A RPI-3 or Quad core RPI is recommended due to video stream threading"
echo "7. Edit the config.py file to tune variables as needed"
echo ""
echo "   cd ~/face-track-demo"
echo "   ./face-track.py"
echo ""
echo "-----------------------------------------------"
echo "See Readme.md for Further Details"
echo $APP_DIR "Good Luck Claude ..."
echo "Bye"
echo ""