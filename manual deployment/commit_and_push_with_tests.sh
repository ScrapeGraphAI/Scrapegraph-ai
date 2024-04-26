if [ $# -eq 0 ]; then
    echo "Usage: $0 <commit_message>"
    exit 1
fi

cd ..

# Extract the commit message from the argument
commit_message="$1"

# Run Pylint on the specified Python files
pylint pylint scrapegraphai/**/*.py scrapegraphai/*.py tests/**/*.py

cd tests

poetry install

# Run pytest
if ! pytest; then
    echo "Pytest failed. Aborting commit and push."
    exit 1
fi

cd ..

# Make the pull
git pull

# Add the modified files to the Git repository
git add .

# Commit the changes with the provided message
git commit -m "$commit_message"

# Push the changes to the remote repository
git push
