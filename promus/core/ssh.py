"""SSH Utilities"""

import os
import re
import sys
import shutil
from os.path import exists
from promus.command import exec_cmd, date, error
PC = sys.modules['promus.core']

RE_USER = re.compile('command="python -m promus greet '
                     '\'(?P<email>.*?),(?P<user>.*?),'
                     '(?P<name>.*?),(?P<alias>.*?)\'" '
                     '(?P<type>.*?) (?P<key>.*?) (?P<desc>.*)')
RE_PENDING = re.compile('command="python -m promus add user '
                        '(?P<email>.*?)" (?P<type>.*?) (?P<key>.*?) '
                        '(?P<desc>.*)')


def make_key(name, cmt=''):
    """Creates a new key. """
    if not exists(name):
        cmd = "ssh-keygen -f %s -C '%s' -N '' -t rsa -q" % (name, cmt)
        exec_cmd(cmd, True)
    return name


def get_keys():
    """Verifies that the keys exist, if not it creates them. Returns
    the path of the keys. """
    alias = PC.config('host.alias')
    if alias == '':
        raise NameError("run `promus setup` to provide an alias")
    home = os.environ['HOME']
    master = os.environ['USER']
    # DEFAULT KEY
    idfname = '%s/.ssh/id_dsa' % home
    if not exists(idfname):
        idfname = '%s/.ssh/id_rsa' % home
        if not exists(idfname):
            cmt = '%s-%s' % (master, alias)
            cmd = "ssh-keygen -f %s -C '%s' -N '' -t rsa -q" % (idfname, cmt)
            exec_cmd(cmd, True)
    # GIT KEY
    fname = '%s/.ssh/%s-%s-git' % (home, master, alias)
    if not exists(fname):
        cmt = '%s-%s-git' % (master, alias)
        cmd = "ssh-keygen -f %s -C '%s' -N '' -t rsa -q" % (fname, cmt)
        exec_cmd(cmd, True)
    return idfname, fname


def get_public_key(private):
    """Retrieve the public key belonging to the given private key. """
    public, _, _ = exec_cmd('ssh-keygen -y -f %s' % private)
    return public.strip()


def read_config():
    """Read the ssh configuration file and return a dictionary with
    its information. """
    config = dict()
    try:
        configf = open('%s/.ssh/config' % os.environ['HOME'], 'r')
    except IOError:
        return config
    for line in configf:
        line = line.split()
        if not line or line[0] == '#':
            continue
        try:
            if line[0] == 'Host':
                entry = ' '.join(line[1:])
                config[entry] = dict()
            else:
                config[entry][line[0]] = line[1]
        except IndexError:
            error("ERROR: check ~/.ssh/config for errors\n")
    configf.close()
    return config


def write_config(config):
    """Write ssh configuration file. """
    last = list()
    configf = open('%s/.ssh/config' % os.environ['HOME'], 'w')
    configf.write('# config file generated on %s\n' % date())
    for entry in config:
        if 'IdentityFile' in config[entry]:
            last.append(entry)
        else:
            configf.write('Host %s\n' % entry)
            for key in config[entry]:
                configf.write('    %s %s\n' % (key, config[entry][key]))
            configf.write('\n')
    for entry in last:
        configf.write('Host %s\n' % entry)
        for key in config[entry]:
            configf.write('    %s %s\n' % (key, config[entry][key]))
        configf.write('\n')
    configf.close()
    exec_cmd('chmod 700 %s/.ssh/config' % os.environ['HOME'], True)


def read_authorized_keys():
    """Read the authorized keys file. """
    users = dict()
    pending = dict()
    unknown = list()
    try:
        usersf = open('%s/.ssh/authorized_keys' % os.environ['HOME'], 'r')
    except IOError:
        return users, pending, unknown
    for line in usersf:
        match = RE_USER.match(line)
        if match:
            if match.group('email') not in users:
                users[match.group('email')] = dict()
            content = [match.group('user'),
                       match.group('name'),
                       match.group('alias'),
                       match.group('type'),
                       match.group('desc')]
            users[match.group('email')][match.group('key')] = content
        else:
            match = RE_PENDING.match(line)
            if match:
                content = [match.group('email'),
                           match.group('type'),
                           match.group('desc')]
                pending[match.group('key')] = content
            else:
                tmp = line.strip()
                if tmp != '' and tmp[0] != '#':
                    unknown.append(line)
    usersf.close()
    return users, pending, unknown


def write_authorized_keys(users, pending, unknown):
    """Rewrite the authorized keys file. """
    ak_file = '%s/.ssh/authorized_keys' % os.environ['HOME']
    backup = '%s/.ssh/authorized_keys.promus-backup' % os.environ['HOME']
    if not os.path.exists(backup):
        shutil.copy(ak_file, backup)
    akfp = open(ak_file, 'w')
    akfp.write('# PROMUS: authorized_keys generated on %s\n' % date())
    emails = sorted(users.keys())
    for user in emails:
        for key, content in users[user].items():
            akfp.write('command="python -m promus greet \'%s,' % user)
            akfp.write('%s,%s,%s\'" ' % (content[0], content[1], content[2]))
            akfp.write('%s %s %s\n' % (content[3], key, content[4]))
    keys = pending.keys()
    if keys:
        akfp.write('# pending requests:\n')
        data = [(key, pending[key][0], pending[key][1]) for key in keys]
        data = sorted(data, key=lambda x: x[1])
        for item in data:
            akfp.write('command="python -m promus add user %s"' % item[1])
            akfp.write(' %s %s %s\n' % (item[2], item[0], item[1]))
    if unknown:
        akfp.write('# unknown keys:\n')
        for entry in unknown:
            akfp.write('%s' % entry)
    akfp.close()
    exec_cmd('chmod 700 %s' % ak_file, True)
