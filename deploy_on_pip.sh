#!/bin/bash

# Install dependencies using Poetry
poetry install

# Check for any potential issues in the project
poetry check

# Build the project
poetry build

# Publish the project to PyPI
poetry publish
