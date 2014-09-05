"""SSH

Here you will find several utilities to manage ssh. In particular
here we can read and write the authorized_keys file as well as the
config file.

"""
import os
import re
import shutil
import os.path as pth
from collections import OrderedDict
from promus.command import exec_cmd
from promus.core import util, git, user

RE_USER_0 = re.compile('command="python -m promus greet '
                       '\'(?P<email>.*?),(?P<user>.*?),'
                       '(?P<name>.*?),(?P<alias>.*?)\'" '
                       '(?P<type>.*?) (?P<key>.*?) (?P<desc>.*)')
RE_USER_1 = re.compile('command="export PROMUS_USER='
                       '\'(?P<email>.*?),(?P<short_key>.*?)\'; '
                       'python -m promus greet" '
                       '(?P<type>.*?) (?P<key>.*?) (?P<desc>.*)')
RE_PENDING = re.compile('command="python -m promus add user '
                        '(?P<email>.*?)" (?P<type>.*?) (?P<key>.*?) '
                        '(?P<desc>.*)')


def make_key(name, cmt=''):
    """Generates a new ssh key if the name is not yet taken. We may
    add a comment to the key with the optional argument. """
    if not pth.exists(name):
        cmd = "ssh-keygen -f %s -C '%s' -N '' -t rsa -q" % (name, cmt)
        exec_cmd(cmd, True)
    return name


def get_keys():
    """Verifies that the default ssh key and git key exists, if not
    it creates them. Returns the path of the keys both keys. """
    master = os.environ['USER']
    alias = git.config('host.alias')
    if alias == '':
        raise NameError("run `promus setup` to provide an alias")
    # DEFAULT KEY
    default_key = pth.expanduser('~/.ssh/id_dsa')
    if not pth.exists(default_key):
        default_key = pth.expanduser('~/.ssh/id_rsa')
        cmt = '%s-%s' % (master, alias)
        make_key(default_key, cmt)
    # GIT KEY
    git_key = pth.expanduser('~/.ssh/%s-%s-git' % (master, alias))
    cmt = '%s-%s-git' % (master, alias)
    make_key(git_key, cmt)
    return default_key, git_key


def get_public_key(private_key):
    """Retrieve the public key belonging to the given private key in
    the file `private_key`. """
    public, _, _ = exec_cmd('ssh-keygen -y -f %s' % private_key)
    return public.strip()


def read_config():
    """Read the ssh configuration file and return a dictionary with
    its information. """
    config = OrderedDict()
    try:
        file_obj = open(pth.expanduser('~/.ssh/config'), 'r')
    except IOError:
        return config
    host = '*'
    config[host] = OrderedDict()
    for line in file_obj:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
        else:
            try:
                key, value = line.lstrip().split(' ', 1)
            except ValueError:
                raise Exception("check ~/.ssh/config for errors.")
        if key == 'Host':
            host = value.strip()
            if host not in config:
                config[host] = OrderedDict()
        else:
            config[host][key] = value.strip()
    file_obj.close()
    return config


def write_config(config):
    """Write ssh configuration file. """
    last = list()
    file_obj = open(pth.expanduser('~/.ssh/config'), 'w')
    file_obj.write('# configuration file generated on %s\n' % util.date())
    for host in config:
        try:
            identity_file = config[host]['IdentityFile']
        except KeyError:
            identity_file = ''
        if 'git' in identity_file:
            last.append(host)
        else:
            file_obj.write('Host {0}\n'.format(host))
            for key in config[host]:
                file_obj.write('    {0} {1}\n'.format(key, config[host][key]))
            file_obj.write('\n')
    for host in last:
        file_obj.write('Host {0}\n'.format(host))
        for key in config[host]:
            file_obj.write('    {0} {1}\n'.format(key, config[host][key]))
        file_obj.write('\n')
    file_obj.close()
    exec_cmd('chmod 700 ~/.ssh/config', True)


def read_authorized_keys():
    """Reads the promus users file and updates it with old entries
    found in the ssh authorized_keys files (if any). Returns the user
    dictionary, the pending requests and the entries not managed by
    promus. """
    users = user.load_users()
    modified = False
    pending = OrderedDict()
    unknown = list()
    try:
        file_obj = open(pth.expanduser('~/.ssh/authorized_keys'), 'r')
    except IOError:
        return users, pending, unknown
    for line in file_obj:
        if RE_USER_1.match(line):
            continue
        match = RE_USER_0.match(line)
        if match:
            modified = True
            email = match.group('email')
            key = match.group('key')
            if email not in users:
                users[email] = dict()
            short_key = key[-10:]
            if short_key not in users[email]:
                users[email][short_key] = dict()
            guest = users[email][short_key]
            guest['user'] = match.group('user')
            guest['name'] = match.group('name')
            guest['alias'] = match.group('alias')
            guest['key_type'] = match.group('type')
            guest['key_desc'] = match.group('desc')
            guest['key'] = key
            continue
        match = RE_PENDING.match(line)
        if match:
            content = [
                match.group('email'),
                match.group('type'),
                match.group('desc'),
            ]
            pending[match.group('key')] = content
            continue
        line = line.strip()
        if line and line[0] != '#':
            unknown.append(line)
    file_obj.close()
    if modified:
        user.dump_users(users)
    return users, pending, unknown


def _write_promus_access(users, file_obj):
    """Helper function for write_authorized_keys. """
    file_obj.write('# PROMUS: file generated on %s\n' % util.date())
    msg = 'command="export PROMUS_USER=\'{email},{short_key}\'; ' \
          'python -m promus greet" {key_type} {key} {key_desc}\n'
    emails = sorted(users.keys())
    for email in emails:
        for short_key, guest in users[email].items():
            fmt_msg = msg.format(
                email=email,
                short_key=short_key,
                key_type=guest['key_type'],
                key=guest['key'],
                key_desc=guest['key_desc']
            )
            file_obj.write(fmt_msg)


def _write_pending_requests(pending, file_obj):
    """Helper function for write_authorized_keys. """
    keys = pending.keys()
    if keys:
        file_obj.write('# pending requests:\n')
        data = [(key, pending[key][0], pending[key][1]) for key in keys]
        data = sorted(data, key=lambda x: x[1])
        for item in data:
            file_obj.write('command="python -m promus add user %s"' % item[1])
            file_obj.write(' %s %s %s\n' % (item[2], item[0], item[1]))


def _write_nonpromus_entries(unknown, file_obj):
    """Helper function for write_authorized_keys. """
    if unknown:
        file_obj.write('# non-promus entries:\n')
        for entry in unknown:
            file_obj.write(entry)
            file_obj.write('\n')


def write_authorized_keys(users, pending, unknown):
    """Rewrite the authorized keys file. This also rewrites the
    users file.

    WARNING: This removes any of the comments that you have written
    in the file. All the data is left intact however.
    """
    ak_file = pth.expanduser('~/.ssh/authorized_keys')
    backup = pth.expanduser('~/.ssh/authorized_keys.promus-backup')
    if not pth.exists(backup):
        shutil.copy(ak_file, backup)
    akfp = open(ak_file, 'w')
    _write_promus_access(users, akfp)
    _write_pending_requests(pending, akfp)
    _write_nonpromus_entries(unknown, akfp)
    akfp.close()
    exec_cmd('chmod 700 %s' % ak_file, True)
    user.dump_users(users)
