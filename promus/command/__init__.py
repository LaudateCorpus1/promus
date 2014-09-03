"""COMMAND

This package is made up of modules to create the command line utility
and a few important functions.

"""

import sys
from subprocess import Popen, PIPE


def error(msg):
    "Print a message to the standard error stream and exit. "
    sys.stderr.write(msg)
    sys.stderr.flush()
    sys.exit(2)


def warn(msg):
    "Print a message to the standard error "
    sys.stderr.write(msg)
    sys.stderr.flush()


def disp(msg):
    "Print a message to the standard output "
    sys.stdout.write(msg)
    sys.stdout.flush()


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
