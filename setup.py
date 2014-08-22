"""promus setup script"""

import imp
import os.path as pt
from setuptools import setup


def get_version():
    "Get version & version_info without importing promus.__init__ "
    path = pt.join(pt.dirname(__file__), 'promus', '__version__.py')
    mod = imp.load_source('promus_version', path)
    return mod.VERSION, mod.VERSION_INFO

VERSION, VERSION_INFO = get_version()

DESCRIPTION = "Remote manager to handle git commands."
LONG_DESCRIPTION = """
Promus is a remote manager designed to create and manage `git`
repositories in a remote server without the need of administrator
privileges.
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


setup(name='promus',
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      keywords='ssh git transfer files collaborate access',
      author='Manuel Lopez',
      author_email='jmlopez.rod@gmail.com',
      url='http://promus.readthedocs.org',
      license='BSD License',
      packages=[
          'promus',
          'promus.command',
          'promus.core',
          ],
      platforms=['Darwin', 'Linux'],
      scripts=['bin/promus'],
      install_requires=[
          'pysftp>=0.2.8',
          'rsa>=3.1.4',
          'pycrypto>=2.6.1',
          'ecdsa>=0.11',
          'python-dateutil>=2.2',
          ],
      package_data={
          'promus.paster': [
              'gitignore.txt',
              'latex/*',
              'python/*',
              ],
          },
      include_package_data=True,
      classifiers=[
          'Development Status :: %s' % DEVSTATUS,
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Communications :: File Sharing',
          'Topic :: Software Development :: Version Control',
          ],
     )
