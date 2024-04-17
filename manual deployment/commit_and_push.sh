#!/bin/bash

# Script: commit_and_push.sh
# Description: This script performs pylint checks on specified Python files,
# adds them to the Git repository, commits the changes with a provided message,
# and pushes the changes to the remote repository.

# Usage: ./commit_and_push.sh <commit_message>
#   <commit_message>: The message to be used for the Git commit. 
#   The commit message should be under ""
# If it is the first time you have to do chmod +x commit_and_push.sh

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <commit_message>"
    exit 1
fi

cd ..
# Extract the commit message from the argument
commit_message="$1"

# Run Pylint on the specified Python files
pylint pylint scrapegraphai/**/*.py scrapegraphai/*.py 
#Make the pull
git pull

# Add the modified files to the Git repository
git add .

# Commit the changes with the provided message
git commit -m "$commit_message"

# Push the changes to the remote repository
git push
