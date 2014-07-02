"""Utility Functions"""

import sys
from os import makedirs
from os.path import exists
from textwrap import TextWrapper
from datetime import datetime
from subprocess import Popen, PIPE
from itertools import chain
from dateutil import parser


def save_password(key, password):
    """Store the email password using a public key. """
    pubkey = '~/.ssh/tmp.pub'
    cmd = 'openssl rsa -in %s -out %s -outform PEM -pubout' % (key, pubkey)
    exec_cmd(cmd)
    passfile = '~/.promus/password.pass'
    cmd = 'echo "%s" | openssl rsautl ' % password
    cmd += '-encrypt -inkey %s -pubin -out %s' % (pubkey, passfile)
    exec_cmd(cmd)


def load_password(key):
    """Retrieve the password using a private key. """
    passfile = '~/.promus/password.pass'
    cmd = 'openssl rsautl -decrypt -inkey %s -in %s' % (key, passfile)
    password, _, _ = exec_cmd(cmd)
    return password.strip()


def user_input(prompt, default):
    "Get an input given a default value. "
    if default != '':
        newval = raw_input("%s (%s): " % (prompt, default))
        if newval == '':
            newval = default
    else:
        newval = default
        while newval == '':
            newval = raw_input("%s: " % prompt)
    return newval.strip()


def wrap_msg(msg, width=70, tab=1):
    "wraps the msg to the specified width and tab indentation. "
    width -= tab*4
    wrapper = TextWrapper(width=width, break_long_words=False)
    tab = '\n%s' % ('    '*tab)
    return tab.join(wrapper.wrap(msg))


def make_dir(path):
    "Create a directory if it does not exist and return True. "
    if exists(path):
        return False
    makedirs(path)
    return True


def parse_list(line, delim=','):
    "Return a list of strings separated by delim. "
    return [item.strip() for item in line.split(delim) if item.strip() != '']


def date(short=False):
    "Return the current date as a string. "
    if isinstance(short, str):
        now = parser.parse(short)
        return now.strftime("%a %b %d, %Y %r")
    now = datetime.now()
    if not short:
        return now.strftime("%a %b %d, %Y %r")
    return now.strftime("%Y-%m-%d-%H-%M-%S")


def exec_cmd(cmd, verbose=False):
    "Run a subprocess and return its output and errors. "
    if verbose:
        out = sys.stdout
        err = sys.stderr
    else:
        out = PIPE
        err = PIPE
    process = Popen(cmd, shell=True, stdout=out, stderr=err)
    out, err = process.communicate()
    return out, err, process.returncode


def tokenizer(string, delim):
    "Return an iterator for `string.split(delim)`. "
    caret = 0
    while True:
        try:
            end = string.index(delim, caret)
        except ValueError:
            yield string[caret:]
            return
        yield string[caret:end]
        caret = end + 1


def merge_lines(str1, str2):
    """The inputs need to be strings separated by the newline character.
    It will return a set containing all the lines. """
    return set(chain(tokenizer(str1, '\n'), tokenizer(str2, '\n')))


def strip(string):
    "Wrapper around the strip function. "
    if string:
        return string.strip()
    return None
