#!/bin/sh
# Installation Script - Installs the waiting room app display
echo 'Beginning Waiting Room System installation ...'
sleep 5

# First update
sudo apt-get update

# Install pip for libraries, SVN for source code, and
# setup virtual environment
sudo apt-get -y install python-pip
sudo apt-get -y install subversion

# Install (if missing) vnc remote desktop
sudo apt-get -y install x11vnc avahi-daemon

sudo pip install virtualenv

# Create log file locations
mkdir ~/WaitingRoomLogs
mkdir ~/WaitingRoomLogs/current
mkdir ~/WaitingRoomLogs/archived

# Set up virtual env for folder
virtualenv WaitingRoomApp

# Fetch the display source code via SVN
cd WaitingRoomApp
. bin/activate
svn export svn://code.aegismed.com/Phase/Source/WaitingRoomApp
cd WaitingRoomApp

# Install all required python libraries for this virtual env
pip install -r requirements.txt

# Install autostart desktop entries
mkdir ~/.config/autostart
mv ./autostart_firefox.desktop ~/.config/autostart/
mv ./autostart_waiting_room_app.desktop ~/.config/autostart/

# Give execute perm to shell script to startup waiting room app
chmod u+x ./autostart_waiting_room_app.sh
chmod o+x ./check_x11vnc_service.sh

# Setup install & update scripts
chmod u+x ./installationscript.sh
mv ./installationscript.sh ~/

chmod u+x ./update-waiting-room-app.sh
mv ./update-waiting-room-app.sh ~/

# Install VNC service
sudo mv ./x11vnc.service /etc/systemd/system/
sudo systemctl enable /etc/systemd/system/x11vnc.service

# Setup PW
sudo touch /etc/x11vnc.pass
sudo chmod 744 /etc/x11vnc.pass
sudo x11vnc -storepasswd g4t0r4d3 /etc/x11vnc.pass

echo 'Finished Waiting Room System Installation!'
sleep 5
