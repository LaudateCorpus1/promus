"""Command

Collection of functions to create the command line utility.

"""

import os
import sys
import os.path as pth
from dateutil import parser
from datetime import datetime
from subprocess import Popen, PIPE


def error(msg):
    "Print a message to the standard error stream and exit. "
    sys.stderr.write(msg)
    sys.exit(2)


def warn(msg):
    "Print a message to the standard error "
    sys.stderr.write(msg)


def disp(msg):
    "Print a message to the standard output "
    sys.stdout.write(msg)


def import_mod(name):
    "Return a module by string. "
    mod = __import__(name)
    for sub in name.split(".")[1:]:
        mod = getattr(mod, sub)
    return mod


def exec_cmd(cmd, verbose=False):
    "Run a subprocess and return its output and errors. "
    if verbose:
        out = sys.stdout
        err = sys.stderr
    else:
        out = PIPE
        err = PIPE
    process = Popen(cmd, shell=True,
                    universal_newlines=True, executable="/bin/bash",
                    stdout=out, stderr=err)
    out, err = process.communicate()
    return out, err, process.returncode


# pylint: disable=E1103
# The reason for this pylint error is that it thinks of
# `now` as a `tuple` instead of a `datetime` object.
def date(short=False):
    "Return the current date as a string. "
    if isinstance(short, str):
        now = parser.parse(str(short))
        return now.strftime("%a %b %d, %Y %r")
    now = datetime.now()
    if not short:
        return now.strftime("%a %b %d, %Y %r")
    return now.strftime("%Y-%m-%d-%H-%M-%S")


def make_dir(path):
    "Create a directory if it does not exist and return True. "
    if pth.exists(path):
        return False
    os.makedirs(path)
    return True


def append_variable(var, val):
    """Return a valid bash string to append a value to a variable. """
    ans = 'if [[ ":$%s:" != *":%s:"* ]]; then\n' % (var, val)
    ans += '    export %s=%s:$%s\n' % (var, val, var)
    return ans + 'fi\n'
