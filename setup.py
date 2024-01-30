from setuptools import setup, find_packages

# Read in the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='amazscraper',
    version='1.0.0', # MAJOR.MINOR.PATCH
    description='A web scraping library using langchain',
    author='Marco Vinciguerra',
    author_email='mvincig11@gmail.com',
    packages=find_packages(),
    install_requires=requirements,
    # Include package data files from MANIFEST.in
    include_package_data=True,
    license='Apache 2.0', 
    # Additional classifiers to help users find the package
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)
