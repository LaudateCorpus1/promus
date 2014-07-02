"""SETUP SCRIPT"""

import sys
import site
from os import uname, environ
from os.path import join, dirname, exists
from setuptools import find_packages, setup
from promus.__version__ import VERSION, VERSION_INFO
from promus.unison import has_unison


DESCRIPTION = "Remote manager to handle commands based on public keys."
LONG_DESCRIPTION = """
Promus is a remote manager designed to create and manage Git
repositories. It does so by executing `git` and `unison` commands on
behalf of a user who has been given authorization via an ssh public
key.
"""

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
SCRIPTS = ['bin/promus', 'bin/%s/promus-find' % PLATFORM]
if not has_unison():
    SCRIPTS.append('bin/%s/unison' % PLATFORM)


setup(name='promus',
      version=VERSION,
      description=DESCRIPTION.strip(),
      long_description=LONG_DESCRIPTION,
      keywords='ssh git unison promus collaborate access',
      author='Manuel Lopez',
      author_email='jmlopez.rod@gmail.com',
      url='http://math.uh.edu/~jmlopez/promus',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      platforms=['Darwin', 'Linux'],
      scripts=SCRIPTS,
      package_data={'promus.git': ['gitignore'],
                    'promus.unison': ['promus-find.cpp'],
                    'promus.paster': ['latex/*', 'python/*'],
                    },
      include_package_data=True,
      classifiers=['Development Status :: %s' % DEVSTATUS,
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Communications :: File Sharing',
                   'Topic :: Software Development :: Version Control',
                   ],
      )
