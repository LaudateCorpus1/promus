"""SETUP SCRIPT"""

from os import uname
from os.path import join, dirname
from setuptools import setup, find_packages
#from promus.__version__ import VERSION, VERSION_INFO

DESCRIPTION = open(join(dirname(__file__), '.git/description')).read()
LONG_DESCRIPTION = open(join(dirname(__file__), 'README.md')).read()
DEV_STATUS_MAP = {
    'alpha': '3 - Alpha',
    'beta': '4 - Beta',
    'rc': '4 - Beta',
    'final': '5 - Production/Stable'
}
if VERSION_INFO[3] == 'alpha' and VERSION_INFO[4] == 0:
    DEVSTATUS = '2 - Pre-Alpha'
else:
    DEVSTATUS = DEV_STATUS_MAP[VERSION_INFO[3]]
PLATFORM = uname()[0]


setup(#name='promus',
      version=VERSION,
      description=DESCRIPTION.strip(),
      long_description=LONG_DESCRIPTION,
      #keywords='keyword1 keyword2',
      #author='your name',
      #author_email='your email',
      #url='your url',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      #scripts = ['bin/script'],
      #package_data = {'': ['submodule/file']},
      classifiers=['Development Status :: %s' % DEVSTATUS,
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   ],
      )
