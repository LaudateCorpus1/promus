"""Setup

Configures git.

"""

import os
import socket
import getpass
import textwrap
import promus.core as prc

DESC = """
this command needs to be run at least once before any of the other
promus commands.

if you have ran this command already and you only wish to modify a
a few settings you may run it again and simply press enter to leave
the values unchanged.

if your server provides you with an email address and you have
entered it as the host email then there is no need to provide a
password. Note however, that if you entered something other than the
email provided by your server (i.e. gmail, hotmail, yahoo) then you
must enter your password.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    subp.add_parser('setup', help='git configuration wizard',
                    formatter_class=raw,
                    description=textwrap.dedent(DESC))


def configure_git(prompt, entry, default=''):
    """Ask user to set value for a git entry. """
    val = prc.config(entry)
    if val == '':
        val = default
    val = prc.user_input(prompt, val.strip())
    return prc.config(entry, val)


def run(_):
    """Run command. """
    prc.check_promus_dependencies()
    prc.config('host.name', socket.gethostname())
    configure_git("Full name", 'user.name')
    configure_git("E-mail address", 'user.email')
    configure_git("Hostname alias", 'host.alias')
    email = configure_git("Host e-mail", 'host.email')
    id_key, _ = prc.get_keys()
    password = getpass.getpass()
    prc.make_dir('%s/.promus' % os.environ['HOME'])
    passfile = '%s/.promus/password.pass' % os.environ['HOME']
    if password != '':
        prc.encrypt_to_file(password, passfile, id_key)
    else:
        if not os.path.exists(passfile):
            prc.encrypt_to_file('', passfile, id_key)
    host_email = email.split(':')[0]
    [username, server] = email.split('@')
    prc.config('host.email', host_email)
    prc.config('host.username', username)
    prc.config('host.smtpserver', 'smtp.%s' % server)
