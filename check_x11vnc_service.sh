#! /bin/bash

# This shell script will check if
# the systemctl's X11VNC service is
# actively running. If it's not this
# script will start the service again
# to allow VNC access to the device.

SERVICE=x11vnc.service

if [ "`systemctl is-active $SERVICE`" != "active" ]
then
    echo Not Running $SERVICE
    systemctl restart $SERVICE
fi

