import os
from setuptools import setup
from pycavi import __version__

if __name__ == '__main__':
    setup(
        name='pycavi',
        python_requires='>=3.11',
        version=os.getenv('PACKAGE_VERSION', __version__),
        packages=['pycavi', 'papi'],
    )
