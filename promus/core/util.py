"""Utility Functions"""

import os
import rsa
import sys
import socket
from os.path import exists, basename
from textwrap import TextWrapper
from itertools import chain
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from promus.command import error
PC = sys.modules['promus.core']
try:
    INPUT = raw_input
except NameError:
    INPUT = input


def is_exe(fpath):
    """Checks to see if the specified path is an executable. """
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def external_executables(ext_exec):
    """Checks to see if your system has access to the executables
    specified by `ext_exec`. It returns a list of the missing and
    found executables. """
    missing = []
    found = []
    for program in ext_exec:
        fpath, _ = os.path.split(program)
        if fpath:
            if is_exe(program):
                found.append(program)
                continue
        else:
            in_path = False
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    found.append(exe_file)
                    in_path = True
                    break
            if in_path:
                continue
        missing.append(program)
    return missing, found


def check_promus_dependencies():
    """This function will terminate the program if it finds that some
    external executables are missing. At the moment there are no
    alternatives as to how to account for their absence. """
    missing, _ = external_executables(['git', 'ssh-keygen'])
    if missing:
        msg = "ERROR: your system is missing the following executables: \n" \
              "    %s \n" \
              "Install them or make sure that they are in your `PATH`.\n"
        error(msg % missing)


def user_input(prompt, default):
    "Get an input given a default value. "
    if default != '':
        newval = INPUT("%s [%s]: " % (prompt, default))
        if newval == '':
            newval = default
    else:
        newval = default
        while newval == '':
            newval = INPUT("%s: " % prompt)
    return newval.strip()


def encrypt_to_file(msg, fname, keyfile):
    """Encrypt msg to file `fname` using the key given by the path
    `keyfile`."""
    with open(keyfile, 'rb') as keyfp:
        keydata = keyfp.read()
    key = rsa.PrivateKey.load_pkcs1(keydata)
    msg = rsa.encrypt(msg.encode('utf-8'), key)
    with open(fname, 'wb') as msgfp:
        msgfp.write(msg)


def decrypt_from_file(fname, keyfile):
    """Decrypt a message in the file `fname` using the key given by
    the path `keyfile`"""
    with open(keyfile, 'rb') as keyfp:
        keydata = keyfp.read()
    key = rsa.PrivateKey.load_pkcs1(keydata)
    with open(fname, 'rb') as msgfp:
        msg = msgfp.read()
    return rsa.decrypt(msg, key).decode('utf-8')


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
    os.makedirs(path)
    return True


def parse_list(line, delim=','):
    "Return a list of strings separated by delim. "
    return [item.strip() for item in line.split(delim) if item.strip() != '']


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


def send_mail(send_to, subject, text, html, files=None):
    """Send an email. `send_to` must be a list of email address to
    which the email will be sent. You can email a `subject` as well
    as two versions of the email: text and html. You may optionally
    attach files by providing a list of them. """
    if not send_to:
        return
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'promus@%s' % socket.gethostname()
    msg['To'] = ','.join(send_to)

    msg.attach(MIMEText(text, 'plain'))
    htmlmsg = MIMEMultipart()
    htmlmsg.attach(MIMEText(html, 'html'))

    if files is None:
        files = []
    for file_ in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_, "rb").read())
        encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % basename(file_))
        htmlmsg.attach(part)
    msg.attach(htmlmsg)
    server = PC.config('host.smtpserver')
    conn = SMTP(server)
    conn.set_debuglevel(False)
    id_key, _ = PC.get_keys()
    passfile = '%s/.promus/password.pass' % os.environ['HOME']
    password = decrypt_from_file(passfile, id_key)
    if password:
        conn.login(PC.config('host.username'), password)
    try:
        conn.sendmail(PC.config('host.email'), send_to, msg.as_string())
    finally:
        conn.close()
