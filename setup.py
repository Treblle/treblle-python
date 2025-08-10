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
    version='2.0.3',
    author='Treblle',
    author_email='support@treblle.com',
    description='Treblle SDK for Django - Production-ready API monitoring and intelligence platform',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Treblle/treblle-python',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: System :: Monitoring',
    ],
    python_requires='>=3.7',
    keywords='treblle api monitoring django middleware observability analytics intelligence devops production thread-safe',
    project_urls={
        'Bug Reports': 'https://github.com/Treblle/treblle-python/issues',
        'Documentation': 'https://docs.treblle.com/en/integrations/django',
        'Source': 'https://github.com/Treblle/treblle-python',
        'Homepage': 'https://treblle.com',
    },
)