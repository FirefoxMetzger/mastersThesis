"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name='RLUnit-database',

    version='0.1.0',

    description=(   "A peewee representation of RLUnit's database. "+
                    "It also features utility scripts for control."),
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/FirefoxMetzger/mastersThesis/tree/master/common',

    # Author details
    author='Sebastian Wallkoetter',
    author_email='sebastian@wallkoetter.net',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='distributed reinforcement learning framework',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['RLUnit_database', 'RLUnit_database.task', 'RLUnit_database.result'],

    # Use requirements found in Requirements.txt
    install_requires=['peewee'],

    # TODO: maybe it makes sense to add some fancy command line tools to control
    # the database
    entry_points={

    },
)
