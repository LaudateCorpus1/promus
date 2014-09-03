"""
this command needs to be run at least once before any of the other
promus commands.

if you have ran this command already and you only wish to modify a
a few settings you may run it again and simply press enter to leave
the values unchanged.

"""

import os
import socket
import getpass
import textwrap
import promus
from promus.command import error
from promus.core import util, git, ssh


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    subp.add_parser('setup', help='git configuration wizard',
                    formatter_class=raw,
                    description=textwrap.dedent(__doc__))


def configure_git(prompt, entry, default=''):
    """Ask user to set value for a git entry. """
    val = git.config(entry)
    if val == '':
        val = default
    val = util.user_input(prompt, val.strip())
    return git.config(entry, val)


def run(_):
    """Run command. """
    missing, _ = util.external_executables(['git', 'ssh-keygen'])
    if missing:
        msg = "ERROR: missing the following executables:\n" \
              "    %s\n" \
              "install them or fix `PATH`\n"
        error(msg % missing)
    git.config('host.name', socket.gethostname())
    configure_git("Full name", 'user.name')
    configure_git("E-mail address", 'user.email')
    configure_git("Hostname alias", 'host.alias')
    email = configure_git("Host e-mail", 'host.email')
    id_key, _ = ssh.get_keys()
    password = getpass.getpass()
    util.make_dir('%s/.promus' % os.environ['HOME'])
    passfile = '%s/.promus/password.pass' % os.environ['HOME']
    if password != '':
        promus.encrypt_to_file(password, passfile, id_key)
    else:
        if not os.path.exists(passfile):
            promus.encrypt_to_file('', passfile, id_key)
    host_email = email.split(':')[0]
    [username, server] = email.split('@')
    git.config('host.email', host_email)
    git.config('host.username', username)
    git.config('host.smtpserver', 'smtp.%s' % server)
