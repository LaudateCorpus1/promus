"""
create the promusrc file and source it in your `.bash_profile` or
`.bashrc` file. This will make sure that bash can find the promus
script.

"""

import sys
import site
import textwrap
import os.path as pth
from promus.command import disp
from promus.core import util, ssh


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    subp.add_parser('install', help='install promus',
                    formatter_class=raw,
                    description=textwrap.dedent(__doc__))


def append_variable(var, val):
    """Return a valid bash string to append a value to a variable. """
    ans = 'if [[ ":$%s:" != *":%s:"* ]]; then\n' % (var, val)
    ans += '    export %s=%s:$%s\n' % (var, val, var)
    return ans + 'fi\n'


def source_promusrc():
    """Source the .promusrc file in the .bashrc file. """
    util.make_dir(pth.expandvars('$HOME/.promus'))
    if sys.platform in ['Darwin', 'darwin']:
        bashrc_path = pth.expandvars('$HOME/.bash_profile')
    else:
        bashrc_path = pth.expandvars('$HOME/.bashrc')
    disp('checking %s ... ' % bashrc_path)
    if pth.exists(bashrc_path):
        expr = [
            'source ~/.promus/promusrc\n',
            'source $HOME/.promus/promusrc\n',
            pth.expandvars('source $HOME/.promus/promusrc\n'),
        ]
        for content_line in open(bashrc_path, 'r'):
            for line in expr:
                if line == content_line:
                    disp('ok\n')
                    return
    with open(bashrc_path, 'a') as content_file:
        disp('\n    including promusrc\n')
        content_file.write('source ~/.promus/promusrc\n')


def promusrc_str():
    """Create the promusrc file contents. """
    userbase = site.getuserbase()
    content = append_variable('PATH', '%s/bin' % sys.prefix)
    content += append_variable('PATH', '%s/bin' % userbase)
    return content


def promusrc():
    """Create the promusrc file. """
    rc_path = pth.expandvars('$HOME/.promus/promusrc')
    disp('writing %s ... ' % rc_path)
    with open(rc_path, 'w') as rcfile:
        rcfile.write(promusrc_str())
    disp('done\n')


def update_ssh_keys():
    """Reads the authorized_keys file and updates it. """
    disp('updating ~/.ssh/authorized_keys\n')
    users, pending, unknown = ssh.read_authorized_keys()
    ssh.write_authorized_keys(users, pending, unknown)


def run(_):
    """Run the command. """
    source_promusrc()
    promusrc()
    update_ssh_keys()
