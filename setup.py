# Always prefer setuptools over distdictionaries
from setuptools import setup, find_packages

# Function to read the contents of a requirements file


def load_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().splitlines()


prod_requirements = load_requirements('requirements.txt')
dev_requirements = load_requirements('requirements-dev.txt')

setup(
    name='scrapegraphai',
    version='0.1.0',  # MAJOR.MINOR.PATCH
    description='A web scraping library based on LangChain which uses LLM and direct graph logic to create scraping pipelines.
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://scrapegraph-ai.readthedocs.io/',
    author='Marco Vinciguerra',
    author_email='mvincig11@gmail.com',
    license='Apache 2.0',
    keywords='langchain, ai, artificial intelligence, gpt, machine learning, ml, nlp, natural language processing, openai, scraping, web scraping, web scraping library, web scraping tool, webscraping',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Scraping',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.9, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*, !=3.8.*',
    include_package_data=True,
    # https://packaging.python.org/en/latest/discussions/install-requires-vs-requirements/
    install_requires=prod_requirements,
    extras_require={
        'dev': prod_requirements + dev_requirements,
    },
)
