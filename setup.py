import setuptools
from os import path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
long_description = ''
if path.exists('README.md'):
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

setuptools.setup(
    name='treblle',
    version='0.014',
    install_requires=['requests'],
    long_description=long_description,
    long_description_content_type="text/markdown",
)