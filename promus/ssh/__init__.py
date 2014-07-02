"""SSH Utilities"""
from os.path import exists
import promus.util as util
import promus.git as git


def make_key(name, cmt=''):
    """Creates a new key. """
    if not exists(name):
        cmd = "ssh-keygen -f %s -C '%s' -N '' -t rsa -q" % (name, cmt)
        util.exec_cmd(cmd, True)
    return name


def get_keys(prs):
    """Verifies that the ssh keys exist, if not then it creates them.
    Returns the path names of the keys. """
    alias = git.gconfig('host.alias')
    if alias == '':
        msg = 'GET_KEYS-ERROR>> use: `promus setup` to give an alias'
        prs.dismiss(msg, 1)
    # DEFAULT KEY
    idfname = '%s/.ssh/id_dsa' % prs.home
    if not exists(idfname):
        idfname = '%s/.ssh/id_rsa' % prs.home
        if not exists(idfname):
            cmt = '%s-%s' % (prs.master, alias)
            cmd = "ssh-keygen -f %s -C '%s' -N '' -t rsa -q" % (idfname, cmt)
            prs.exec_cmd(cmd, True)
    fname = '%s/.ssh/%s-%s-git' % (prs.home, prs.master, alias)
    if not exists(fname):
        cmt = '%s-%s-git' % (prs.master, alias)
        cmd = "ssh-keygen -f %s -C '%s' -N '' -t rsa -q" % (fname, cmt)
        prs.exec_cmd(cmd, True)
    return idfname, fname


def get_public_key(private):
    """Retrieve the public key belonging to the given private key. """
    public, _, _ = util.exec_cmd('ssh-keygen -y -f %s' % private)
    return public.strip()


def read_config(prs):
    """Read the ssh configuration file and return a dictionary with
    its information. """
    config = dict()
    try:
        configf = open('%s/.ssh/config' % prs.home, 'r')
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
            prs.dismiss('SSH_CONFIG-ERROR>> check .ssh/config for errors', 1)
    configf.close()
    return config


def write_config(prs, config):
    """Write ssh configuration file. """
    last = list()
    configf = open('%s/.ssh/config' % prs.home, 'w')
    configf.write('# config file generated on %s\n' % util.date())
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
    util.exec_cmd('chmod 700 ~/.ssh/config', True)


def read_authorized_keys(prs):
    """Read the authorized keys file. """
    users = dict()
    unknown = list()
    try:
        usersf = open('%s/.ssh/authorized_keys' % prs.home, 'r')
    except IOError:
        return users
    for line in usersf:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        entry = line.split('ssh-')
        start = entry[0]
        try:
            tmp = entry[1].split()
            sshtype = tmp[0]
            key = tmp[1]
            user, host  = tmp[2].split('@')
        except (IndexError, ValueError):
            unknown.append(line)
        else:
            info = dict()
            info['start'] = start
            info['type'] = sshtype
            info['key'] = key
            info['host'] = host
            if user in users:
                users[user].append(info)
            else:
                users[user] = [info]
    usersf.close()
    return users, unknown


def write_authorized_keys(prs, users, unknown):
    """Rewrite the authorized keys file. """
    last = list()
    usersf = open('%s/.ssh/authorized_keys' % prs.home, 'w')
    usersf.write('# authorized_keys file generated on %s\n' % util.date())
    for user, info in users.items():
        for val in info:
            if val['start']:
                start = '%s ' % val['start']
            else:
                start = ''
            entry = '%sssh-%s %s %s@%s' % (start, val['type'], 
                                           val['key'], user, val['host'])
            usersf.write('%s\n' % entry)  
    usersf.write('# unknown or temporary keys\n')                        
    for entry in unknown:
        usersf.write('%s\n' % entry)
    usersf.close()
    util.exec_cmd('chmod 700 ~/.ssh/authorized_keys', True)
    