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
    version='2.0.0b1',
    author='Treblle',
    author_email='info@treblle.com',
    description='Treblle SDK for Django - API monitoring and observability',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Treblle/treblle-python',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: System :: Monitoring',
    ],
    python_requires='>=3.7',
    install_requires=['requests>=2.25.0', 'Django>=2.2'],
    keywords='treblle api monitoring django middleware observability',
    project_urls={
        'Bug Reports': 'https://github.com/Treblle/treblle-python/issues',
        'Documentation': 'https://docs.treblle.com/en/integrations/django',
        'Source': 'https://github.com/Treblle/treblle-python',
        'Homepage': 'https://treblle.com',
    },
)