#!/bin/sh

# Make sure to:
# 1) Name this file `backup.sh` and place it in /home/ubuntu
# 2) Run sudo apt-get install awscli to install the AWSCLI
# 3) Run aws configure (enter s3-authorized IAM user and specify region)
# 4) Fill in DB host + name
# 5) Create S3 bucket for the backups and fill it in below (set a lifecycle rule to expire files older than X days in the bucket)
# 6) Run chmod +x backup.sh
# 7) Test it out via ./backup.sh
# 8) Set up a daily backup at midnight via `crontab -e`:
#    0 0 * * * /home/ubuntu/backup.sh > /home/ubuntu/backup.log

# DB host (secondary preferred as to avoid impacting primary performance)
HOST=127.0.0.1

# DB name
DBNAME=bgg

# S3 bucket name
BUCKET=bgg-comments

# Linux user account
USER=micahshanks

# Current time
TIME=`/bin/date +%d-%m-%Y-%T`

# Backup directory
DEST=//Users/$USER/tmp

# Tar file of backup directory
TAR=$DEST/../$TIME.tar

# Create backup dir (-p to avoid warning if already exists)
/bin/mkdir -p $DEST

# Log
echo "Backing up $HOST/$DBNAME to s3://$BUCKET/ on $TIME";

# Dump from mongodb host into backup directory
/usr/local/Cellar/mongodb/3.4.4/bin/mongodump -h $HOST -d $DBNAME -o $DEST

# Create tar of backup directory
tar cvf $TAR -C $DEST .

# Upload tar to s3
aws s3 cp $TAR s3://$BUCKET/

# Remove tar file locally
/bin/rm -f $TAR

# Remove backup directory
/bin/rm -rf $DEST

# All done
echo "Backup available at https://s3.amazonaws.com/$BUCKET/$TIME.tar"
