# !/bin/bash

# Script will backup/copy the log files under ~/WaitingRoomLogs/current/
# to ~/WaitingRoomLogs/archived.

# For each log file, let's copy them into the Archived folder.
LOG_CURRENT_DIR=/home/odroid/WaitingRoomLogs/current/*
LOG_ARCHIVED_DIR=/home/odroid/WaitingRoomLogs/archived/

for log_file in $LOG_CURRENT_DIR
do
   # Log file format: archived dir + date + log file name 
   
   cp $log_file $LOG_ARCHIVED_DIR`date +"%Y_%m_%d-%H_%M_%S"`-${log_file##*/}

   # Remove the file after it's been copied
   rm $log_file
    

done
