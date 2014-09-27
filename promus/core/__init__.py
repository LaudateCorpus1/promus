"""CORE

This package contains the object that executes commands on your
behalf as well as other utility functions.

"""
import re
import os
import sys
import json
import socket
import inspect
import os.path as pth
from textwrap import TextWrapper
from promus.command import warn, error, c_msg
from . import util, git

MASTER = {
    'user': os.environ['USER'],
    'name': git.config('user.name'),
    'email': git.config('user.email'),
    'host': socket.gethostname(),
    'alias': git.config('host.alias'),
}


def load_users(user_file='~/.promus/users'):
    """Gather the information from the file specified by user_file.
    This is a file in the form:

        {
            "email": {
                "short-key": {
                    "property1": "value1",
                    "property2": "value2"
                }
            },
            "email2": {
                "short-key": {
                    "property1": "value1",
                    "property2": "value2"
                }
            }
        }

    returns a dictionary of users."""
    try:
        file_obj = open(pth.expanduser(user_file), 'r')
    except IOError:
        return dict()
    try:
        users = json.load(file_obj)
    except ValueError:
        return dict()
    file_obj.close()
    return users


def dump_users(users, users_file='~/.promus/users'):
    """Stores the `users` dictionary in the specified `users_file`."""
    with open(pth.expanduser(users_file), 'w') as fp_:
        json.dump(
            users,
            fp_,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )


# pylint: disable=too-many-instance-attributes
class User(object):
    """A user object is used to access the information about a
    particular individual who logged in to the server. """

    def __init__(self):
        self.user = ''
        self.name = ''
        self.email = ''
        self.host = ''
        self.alias = ''
        self.key = None
        self.key_type = None
        self.key_desc = None
        self.cmd = None
        self.cmd_token = None
        self.cmd_name = None
        self.cmd_ok = False

    def is_master(self):
        """Return True if the user e-mail matches the masters
        e-mail."""
        if self.email == MASTER['email']:
            return True
        return False

    def has_access(self, acl):
        """The parameter acl should be a list containing user emails,
        usernames or names along with the keywords `!allow`, `!deny`
        and `!all`. For insance:

            ['!deny', '!all', '!allow', 'user1']

        denies access to everyone except user1. The acl

            ['!deny', 'user1', '!allow', 'user2', 'user1]

        gives access to user1 even though it was first explicitly
        denied.

        By default all acls allow access all users. That is the
        default action is `!allow`. The keyword `!all` is prefered to
        be used in all acl to first deny or allow access to all users
        and then restrict only a few. """
        action = '!allow'
        access = True
        email = self.email.lower()
        username = self.user.lower()
        name = self.name.lower()
        for item in acl:
            item = item.lower()
            if item in ['!deny', '!allow']:
                action = item
                continue
            if item in ['!all', email, username] or item in name:
                if action == '!allow':
                    access = True
                else:
                    access = False
        return access


def get_promus_user():
    """Attempts to obtain the current user by looking through the
    file `~/.promus/users` for the information contained by the
    environmental variable `PROMUS_USER`."""
    if 'PROMUS_USER' not in os.environ:
        raise RuntimeError("PROMUS_USER was not set.")
    email, short_key = os.environ['PROMUS_USER'].split(',')
    users = load_users()
    try:
        user = users[email][short_key]
    except KeyError:
        msg = "PROMUS_USER[%s] not found" % os.environ['PROMUS_USER']
        raise RuntimeError(msg)
    promus_user = User()
    promus_user.user = user.get('user', '')
    promus_user.name = user.get('name', '')
    promus_user.email = email
    promus_user.host = user.get('host', '')
    promus_user.alias = user.get('alias', '')
    promus_user.key = user.get('key', '')
    promus_user.key_type = user.get('key_type', '')
    promus_user.key_desc = user.get('key_desc', '')
    promus_user.cmd = os.environ.get('SSH_ORIGINAL_COMMAND', '')
    if re.search('.*?[;&|]', promus_user.cmd):
        promus_user.cmd_ok = False
    else:
        promus_user.cmd_ok = True
    promus_user.cmd_token = util.split_at(' ', promus_user.cmd)
    try:
        promus_user.cmd_name = promus_user.cmd_token[0]
    except IndexError:
        promus_user.cmd_name = ''
    return promus_user


def get_master_user():
    """Creates a User object using the information stored in
    MASTER."""
    master = User()
    master.user = MASTER['user']
    master.name = MASTER['name']
    master.email = MASTER['email']
    master.host = MASTER['host']
    master.alias = MASTER['alias']
    master.key = ''
    master.key_type = ''
    master.key_desc = ''
    return master


class Promus(object):
    """Handle commands issued over ssh."""

    def __init__(self):
        self.guest = None
        self._path = pth.expanduser('~/.promus')
        util.make_dir(self._path)
        self._log_file = open('{0}/promus.log'.format(self._path), 'a')

    def log(self, sender, msg, color=None):
        """Write a message to the log file. """
        fmt = "{0}{1} {2}\n"
        if color:
            fmt = fmt.format(
                c_msg('BD', '[PROMUS]: '),
                c_msg('B'+color, sender.upper()+">>"),
                c_msg(color, msg)
            )
            warn(fmt)
        else:
            fmt = fmt.format(
                c_msg('BD', '[PROMUS]: '),
                sender.upper()+">>",
                msg
            )
            warn(fmt)
        msg = '[{date}:~ {guest}:{key}]$ {sender}>> {msg}\n'.format(
            date=util.date(True),
            guest=self.guest.email,
            sender=sender.upper(),
            msg=msg,
            key=self.guest.key[-10:],
        )
        self._log_file.write(msg)

    def dismiss(self, sender, msg, status=0):
        """Print msg to the standard error stream as well as to the
        log file and exit with the provided status. """
        if status != 0:
            self.log(sender+"-ERROR", msg, 'R')
        else:
            self.log(sender, msg)
        self._log_file.close()
        sys.exit(status)

    def greet(self):
        """Handle the guest request. """
        try:
            self.guest = get_promus_user()
        except RuntimeError as exception:
            msg = "unable to greet guest: {0}"
            self.dismiss('greet', msg.format(exception.message), 1)
        self.log('greet', "connected as {0}".format(self.guest.email))
        if not self.guest.cmd_ok:
            msg = "more than one command: {0}"
            self.dismiss('greet', msg.format(self.guest.cmd), 1)
        if self.guest.cmd_name == '':
            msg = "no interactive shell allowed"
            self.dismiss('greet', msg, 1)
        self.log('greet', "command: %r" % self.guest.cmd)
        token = self.guest.cmd_token
        if self.guest.cmd_name == '__DOC__':
            _show_doc(self, token[1])
        elif self.guest.cmd_name == '__PYFUNC__':
            _exec_pyfunc(self, token[1], token[2:])
        else:
            _exec_wrapper(self, token[0])
        self.dismiss('greet', "done", 0)

    def attend_guest(self):
        """After the greeting is over the connection is still active
        and several other subprocess get called. This method sets the
        guest so that promus may know whom it is attending."""
        try:
            self.guest = get_promus_user()
        except RuntimeError as exception:
            msg = "unable to attend guest: {0}"
            self.dismiss('attend_guest', msg.format(exception.message), 1)

    def attend_master(self):
        """Some hooks require the promus guest to be the master. """
        self.guest = get_master_user()


from . import cmd


def _show_doc(prs, func):
    """Display the documentation for the function."""
    if func in cmd.PY_MAP:
        info = cmd.PY_MAP[func]
    elif func in cmd.CMD_MAP:
        info = cmd.CMD_MAP[func]
    else:
        prs.dismiss('show_doc', "'%s' is not defined" % func, 1)
    if not prs.guest.has_access(info[1]):
        prs.dismiss('show_doc', "access denied to '%s'" % func, 1)
    pyfunc = info[0]
    argspec = inspect.getargspec(pyfunc)
    func_doc = "\n{func}{space}{args}:\n    {doc}\n\n".format(
        func=c_msg("BD", func),
        space=' ' if len(argspec[0][1:]) > 0 else '',
        args=', '.join(argspec[0][1:]),
        doc=pyfunc.__doc__
    )
    warn(func_doc)


# pylint: disable=star-args
def _exec_pyfunc(prs, func, args):
    """Execute the python function."""
    if func not in cmd.PY_MAP:
        prs.dismiss('exec_pyfunc', "'%s' is not defined" % func, 1)
    if not prs.guest.has_access(cmd.PY_MAP[func][1]):
        prs.dismiss('exec_pyfunc', "access denied to '%s'" % func, 1)
    try:
        cmd.PY_MAP[func][0](prs, *args)
    except TypeError as exception:
        prs.dismiss('exec_pyfunc', "%s" % exception.message, 1)


def _exec_wrapper(prs, prog):
    """Execute the wrapper for the executable."""
    if prog not in cmd.CMD_MAP:
        prs.dismiss('exec_wrapper', "'%s' is not defined" % prog, 1)
    if not prs.guest.has_access(cmd.CMD_MAP[prog][1]):
        prs.dismiss('exec_wrapper', "access denied to '%s'" % prog, 1)
    cmd.CMD_MAP[prog][0](prs)
