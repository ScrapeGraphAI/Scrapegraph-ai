#!/bin/bash
cd ..

rye self update
# Install dependencies using Poetry
rye sync

# Build the project
rye build

# Publish the project to PyPI
rye publish
