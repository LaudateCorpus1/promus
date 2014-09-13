"""CMD

Provides several functions to execute on behalf of the git user. This
functionality is extendible and can be added on the file
`~/.promus/commands.py`.

NOTE: Quotes must be escaped.

"""
import socket
import promus
import os.path as pth
from imp import load_source
from promus.core import util, user
from promus.command import disp, exec_cmd


def exec_scp(prs):
    """You (the git user) are allowed to send and receive files
    through `scp`. There is one catch: You must place the file in
    `~/promus-box/git_user_name/` where `git_user_email` is the email
    you identify with.

    This means that you may execute:

        scp file host:~/promus-box/git_user_email/file

    or

        scp host:~/promus-box/git_user_email/file file

    or

        promus send file host file

    """
    guest = prs.guest
    token = guest.cmd_token
    if len(token) != 3 or token[1] not in ['-t', '-f']:
        prs.dismiss('exec_scp', 'invalid scp command ... ', 1)
    file_name = pth.expanduser(token[2])
    file_name = pth.expandvars(file_name)
    dir_name = pth.expanduser('~/promus-box/%s/' % guest.email)
    if not file_name.startswith(dir_name):
        prs.dismiss('exec_scp', 'file not in %r' % dir_name, 1)
    util.make_dir(dir_name)
    if token[1] == '-t':
        prs.log('exec_scp', 'receiving ... ')
        msg = exec_scp.success_msg.format(
            master_name=user.MASTER['name'],
            master_host=user.MASTER['host'],
            guest_name=guest.name,
            action='sent you',
            file_name=file_name,
            host_name=guest.host,
            whereabouts='from',
            alias=guest.alias,
        )
    elif token[1] == '-f':
        prs.log('exec_scp', 'sending ... ')
        msg = exec_scp.success_msg.format(
            master_name=user.MASTER['name'],
            master_host=user.MASTER['host'],
            guest_name=guest.name,
            action='received',
            file_name=file_name,
            host_name=guest.host,
            whereabouts='on',
            alias=guest.alias,
        )
    _, _, exit_code = exec_cmd(guest.cmd, True)
    if exit_code == 0:
        prs.log('exec_scp', 'notifying %s ... ' % user.MASTER['name'])
        try:
            promus.send_mail(
                [user.MASTER['email']],
                'File transfer successful',
                msg,
                None
            )
        except socket.gaierror:
            prs.dismiss('exec_scp', 'unable to send email', 1)
        prs.log('exec_scp', 'email sent to %r' % user.MASTER['email'])
    else:
        prs.dismiss('exec_scp', 'exit code %r ... ' % exit_code, 1)


exec_scp.success_msg = """Hello {master_name},

This message is to inform you that {guest_name} has {action} the
file

    {master_host}:{file_name}

{whereabouts}

    {host_name} ({alias})

- Promus

"""


def say_hi(prs, msg):
    """Test function, a guest will send a message. """
    disp('Hi %s, your message was: %s\n' % (prs.guest.name, msg))


CMD_MAP = {
    'scp': (exec_scp, ['!allow', '!all']),
}
PY_MAP = {
    'say_hi': (say_hi, ['!allow', 'all']),
}
USER_CMD_PATH = pth.expanduser('~/.promus/cmd.py')
if pth.exists(USER_CMD_PATH):
    USER_CMD = load_source('promus_user_cmd', USER_CMD_PATH)
    try:
        PY_MAP.update(USER_CMD.PY_MAP)
    except AttributeError:
        pass
    try:
        CMD_MAP.update(USER_CMD.CMD_MAP)
    except AttributeError:
        pass
