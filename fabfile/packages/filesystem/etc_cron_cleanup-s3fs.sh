#!/bin/sh
#
# Clean up script for /tmp folder
# 5/22/20 CG
# https://gitlab.com/{_project_name}/main/-/issues/695
#
# We are putting this inside the /etc/cron.daily folder

# - Make sure permissions are set correctly: +x
# - Make sure the file has no extension (remove .sh at the end)
#
# This is to make sure the files in /tmp that is being used
# for the S3 cache is not taking up too much space because
# we are using `ensure_diskfree=10240` so the entire server
# does not die due to out of disk space
#
# Our current plan is to delete files every 30 days but that
# could change depending on how much files get deleted
# We want to have the server keep the files longer if we can
# but we have to observe how much disk space is free once
# we run this daily and see if we can back off the # days
# to higher than 30 days
#
# References
# https://www.cyberciti.biz/cloud-computing/why-is-my-linux-unix-crontab-job-not-working/
#
# Example:
# sudo find /tmp/s3fs.{_project_name}.com -mtime +90 -exec rm -rf {} \;
# sudo find /tmp/s3fs.{_project_name}.com -type d -empty -delete
#
# 8/4/20 CG: We are now doing this at +21 days
# sudo find /tmp/s3fs.{_project_name}.com -mtime +21 -exec rm -rf {} \;
# 2/19/21 CG: We are doing this at +14 days
# sudo find /tmp/s3fs.{_project_name}.com -mtime +14 -exec rm -rf {} \;
#
# You can also run unix commands remotely
#
# ssh {_project_name}@prd-www8.{_project_name}.com df -h
#
# will show you the output on your local terminal
#

# (1) Set the PATH and DAYS
# Example is DIR=/tmp/s3fs

DIR=/tmp/{{bucket_name}}
DAYS={{days}}
HOST=$(/bin/hostname)
#FILE_LOG=/mnt/s3fs/tmp/cleanup-s3fs/$HOST.files.log
#RUN_LOG=/mnt/s3fs/tmp/cleanup-s3fs/$HOST.run.log
FILE_LOG=/tmp/cleanup.files.log
RUN_LOG=/tmp/cleanup.run.log

# ------------------------------------------------------------

# (2) Pump out what we are going to find into a file
find $DIR -mtime "+$DAYS" -exec ls -ltrh {} \; > $FILES_LOG

# (3) Run the cleanup
find $DIR -mtime "+$DAYS" -exec rm -rf {} \;

# (4) Also delete empty directories
find $DIR -type d -empty -delete

# (5) Count the files that are deleted and save to the cleanup log
NOW=$(date +"%D %T")
COUNT=$(cat "$FILES_LOG" | wc -l)
echo "$NOW | $COUNT files deleted" >> $RUN_LOG

# (6) Post to server
df | curl --data-urlencode df@- https://{_project_name}.com/api/chrome/server/disk_usage
