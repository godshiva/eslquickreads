#!/bin/bash

# Get the current date and time
now=$(date +"%Y-%m-%d_%H-%M-%S")

# Specify the filename with the current datetime
filename="$now.txt"

# Execute the command and pipe the output to the file
mysqldump -u algorithmguy -h algorithmguy.mysql.pythonanywhere-services.com 'algorithmguy$default' --set-gtid-purged=OFF --no-tablespaces  > "backups/$filename.sql"