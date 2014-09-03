"""UTIL

Set of very basic functions to aid in the development of other promus
modules.

"""

import os
import os.path as pth
from itertools import chain
from dateutil import parser
from datetime import datetime
try:
    INPUT = raw_input
except NameError:
    INPUT = input


def is_exe(fpath):
    """Returns true if the specified path is an executable. """
    return pth.isfile(fpath) and os.access(fpath, os.X_OK)


def external_executables(ext_exec):
    """Checks to see if your system has access to the executables in
    the list specified by `ext_exec`. It returns a list of the
    missing and found executables. """
    missing = list()
    found = list()
    for program in ext_exec:
        fpath, _ = pth.split(program)
        if fpath:
            if is_exe(program):
                found.append(program)
                continue
        else:
            in_path = False
            sys_path = os.environ["PATH"].split(os.pathsep)
            for path in sys_path:
                path = path.strip('"')
                exe_file = pth.join(path, program)
                if is_exe(exe_file):
                    found.append(exe_file)
                    in_path = True
                    break
            if in_path:
                continue
        missing.append(program)
    return missing, found


def user_input(prompt, default):
    """Prompt a message asking for an input. If a default value is
    given it will be displayed and returned if no input is entered."""
    if default != '':
        newval = INPUT("{0} [{1}]: ".format(prompt, default))
        if newval == '':
            newval = default
    else:
        newval = default
        while newval == '':
            newval = INPUT("{0}: ".format(prompt))
    return newval.strip()


def make_dir(path):
    """Create a directory if it does not exist and return True.
    Othewise return False. """
    if pth.exists(path):
        return False
    os.makedirs(path)
    return True


def split_at(delimiter, text, opens='<(', closes='>)', quotes='"\''):
    """Custom function to split at commas. Taken from stackoverflow
    http://stackoverflow.com/a/20599372/788553"""
    result = []
    buff = ""
    level = 0
    is_quoted = False
    for char in text:
        if char in delimiter and level == 0 and not is_quoted:
            result.append(buff)
            buff = ""
        else:
            buff += char
            if char in opens:
                level += 1
            elif char in closes:
                level -= 1
            elif char in quotes:
                is_quoted = not is_quoted
    if not buff == "":
        result.append(buff)
    return result


def _tokenizer(string, delim):
    """Return an iterator for `string.split(delim)`. """
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
    """The inputs need to be strings separated by the newline
    character. It will return a set containing all the lines. """
    return set(chain(_tokenizer(str1, '\n'), _tokenizer(str2, '\n')))


# pylint: disable=maybe-no-member
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


def strip(msg):
    """Wrapper around the strip atribute for strings. Returns None if
    it msg is not valid."""
    try:
        return msg.strip()
    except AttributeError:
        return None
