"""USER

This module provides functions to manage the users that log in to the
server.

"""
import os
import re
import socket
import json
import os.path as pth
from promus.core import util, git

MASTER = {
    'user': os.environ['USER'],
    'name': git.config('user.name'),
    'email': git.config('user.email'),
    'host': socket.gethostname(),
    'alias': git.config('host.alias'),
}


def load_users():
    """Gather the information from the file `~/.promus/users`. This
    is a file in the form:

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
        file_obj = open(pth.expanduser('~/.promus/users'), 'r')
    except IOError:
        return dict()
    try:
        users = json.load(file_obj)
    except ValueError:
        return dict()
    file_obj.close()
    return users


def dump_users(users):
    """Stores the users dictionary in the file `~/.promus/users`."""
    with open(pth.expanduser('~/.promus/users'), 'w') as fp_:
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

    def allow_edit(self, acl, path):
        """Checks to see if the user can make an edit to the path
        based on the values on the acl. """
        pass


def get_promus_user():
    """Attempts to obtain the current user by looking through the
    file `~/.promus/users` for the information contained by the
    environmental variable `PROMUS_USER`."""
    if 'PROMUS_USER' not in os.environ:
        raise RuntimeError("PROMUS_USER was not set.")
    if 'SSH_ORIGINAL_COMMAND' not in os.environ:
        raise RuntimeError("SSH_ORIGINAL_COMMAND was not set.")
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
    promus_user.cmd = os.environ['SSH_ORIGINAL_COMMAND']
    if re.search('.*?[;&|]', promus_user.cmd):
        promus_user.cmd_ok = False
    else:
        promus_user.cmd_ok = True
    promus_user.cmd_token = util.split_at(' ', promus_user.cmd)
    promus_user.cmd_name = promus_user.cmd_token[0]
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
    return master
