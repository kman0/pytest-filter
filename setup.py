__author__ = 'M'
from setuptools import setup
import codecs

VERSION = '0.2dev'
PYPI_VERSION = '0.1'
DESCRIPTION = (
    'filters/excludes tests using .ini files'
)

setup(
    name='pytest-filter',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    version=VERSION,
    url='https://github.com/manojklm/pytest-filter/',
    download_url='https://github.com/manojklm/pytest-filter/tarball/%s' % PYPI_VERSION,
    license='MIT',
    author='mk',
    author_email='manojklm@gmail.com',
    entry_points={'pytest11': ['filter = pytest_filter']},
    py_modules=['pytest_filter'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['pytest>=2.6'],
    classifiers=[
        'Environment :: Plugins',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
