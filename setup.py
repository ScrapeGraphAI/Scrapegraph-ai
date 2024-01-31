# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='amazscraper',
    version='0.1.0', # MAJOR.MINOR.PATCH
    description='A web scraping library using langchain',
    long_description='A web scraping library using langchain but a longer description',
    long_description_content_type='text/markdown',
    url='https://amazscraper.readthedocs.io/',
    author='Marco Vinciguerra',
    author_email='mvincig11@gmail.com',
    license='Apache 2.0', 
    keywords='langchain, ai, artificial intelligence, gpt, machine learning, ml, nlp, natural language processing, openai, scraping, web scraping, web scraping library, web scraping tool, webscraping',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Scraping',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
    packages = ['amazscraper'],
    include_package_data=True,
    # https://packaging.python.org/en/latest/discussions/install-requires-vs-requirements/
    install_requires=[
        'beautifulsoup4',
        'langchain',
        'langchain_core',
        'langchain_openai',
        'python-dotenv',
        'Requests',
        'pytest',
    ]
)
