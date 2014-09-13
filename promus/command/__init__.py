"""COMMAND

This package is made up of modules to create the command line utility
and a few important functions.

"""

import sys
from subprocess import Popen, PIPE
COLOR = {
    'BD': '1',
    'R': '31',
    'G': '32',
    'Y': '33',
    'B': '34',
    'M': '35',
    'C': '36',
    'BR': '1;31',
    'BG': '1;32',
    'BY': '1;33',
    'BB': '1;34',
    'BM': '1;35',
    'BC': '1;36',
}


def c_msg(color, msg):
    """Return a message in the color specified."""
    return '\033[%sm%s\033[0m' % (COLOR[color], msg)


def error(msg):
    "Print a message to the standard error stream and exit. "
    sys.stderr.write(msg)
    sys.stderr.flush()
    sys.exit(2)


def c_error(msg):
    """Print a color message to the standard error stream and exit.
    The message is written in the form: "ERROR: msg\\n" with all
    characters in red. """
    sys.stderr.write(c_msg('BR', 'ERROR: '))
    sys.stderr.write(c_msg('R', msg+'\n'))
    sys.stderr.flush()
    sys.exit(2)


def warn(msg):
    "Print a message to the standard error "
    sys.stderr.write(msg)
    sys.stderr.flush()


def c_warn(msg):
    """Print a color message to the standard error stream. The
    message is written in the form: "WARNING: msg\\n" with all
    characters in yellow. """
    sys.stderr.write(c_msg('BY', 'WARNING: '))
    sys.stderr.write(c_msg('Y', msg+'\n'))
    sys.stderr.flush()


def disp(msg):
    "Print a message to the standard output "
    sys.stdout.write(msg)
    sys.stdout.flush()


def c_disp(color, msg):
    """Print a color message to the stardard output stream. """
    sys.stdout.write(c_msg(color, msg))
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
