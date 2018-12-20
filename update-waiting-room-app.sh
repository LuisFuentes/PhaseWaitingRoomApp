#!/bin/sh
# Update waiting room app script - Updates the waiting room app

echo 'Updating the Waiting Room App...'
sleep 5
echo 'Removing old code...'
# Fetch the display source code via SVN
cd ~/WaitingRoomApp
# Remove old code repo
rm -r WaitingRoomApp

echo 'Updating with new code...'
# Update with new source code
svn export svn://code.aegismed.com/Phase/Source/WaitingRoomApp
cd WaitingRoomApp

echo 'Finished updating code base'
echo 'Updating the upstart scripts...'
# Update autostart scripts (if changed)
mv ./start-waiting-room-app.conf ~/.config/upstart/
mv ./start-firefox-display.conf ~/.config/upstart/
echo 'Finished updating the upstart scripts!'

echo 'Finished running the update script! Closing in 5 seconds...'
sleep 5