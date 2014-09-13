"""GIT

In this package we can find functions designed to obtain information
from a git repository.

"""
import json
import os.path as pth
from fnmatch import fnmatch
from promus.command import exec_cmd
from promus.core import util


class ACLException(Exception):
    """Raised when parsing an ACL string. """
    pass


class NoACLException(Exception):
    """Raised solely when the git repository cannot find the acl
    file. """
    pass


class ProfileException(Exception):
    """Raised when parsing a profile string. """
    pass


class NoProfileException(Exception):
    """Raised when the git repository cannot find a guest profile. """
    pass


def config(entry, val=None, global_setting=True):
    """Call `git config --global` when `global_setting` is set to
    True, otherwise call `git config` to set or get an entry. """
    cmd = 'git config '
    if global_setting:
        cmd += '--global '
    if val:
        exec_cmd('{0} {1} "{2}"'.format(cmd, entry, val))
    else:
        val, _, _ = exec_cmd('{0} {1}'.format(cmd, entry))
    return util.strip(val)


def describe():
    "Return last tag, number of commits and sha. "
    out, _, status = exec_cmd('git describe --long')
    if status != 0:
        return None, 0, None
    out = out.split('-')
    return out[0], out[1], out[2][1:]


def repo_name(local=True):
    "Return the name of the repository. "
    if local:
        cmd = 'basename `git rev-parse --show-toplevel`'
    else:
        cmd = 'basename `pwd`'
    out, _, _ = exec_cmd(cmd)
    return util.strip(out)


def local_path():
    "Return the path to directory containing the `.git` directory. "
    out, _, _ = exec_cmd('git rev-parse --show-toplevel')
    return util.strip(out)


def remote_path():
    "Return the path of the remote repository. "
    out, _, _ = exec_cmd('git config --get remote.origin.url')
    return util.strip(out)


HOOK_TEMPLATE = '''#!/usr/bin/env python
"""{hook} hook generated on {date}"""
from promus.core import Promus
import promus.hooks.{hookpy} as hook

if __name__ == "__main__":
    PRS = Promus()
    hook.run(PRS)
    PRS.dismiss("{hook}", "done", 0)
'''


def make_hook(hook, path):
    "Creates the specified hook. "
    hook_file = "%s/%s" % (path, hook)
    if pth.exists(hook_file):
        cmd = "mv %s %s.%s" % (hook_file, hook_file, util.date(True))
        exec_cmd(cmd, True)
    hookpy = hook.replace('-', '_')
    content = HOOK_TEMPLATE.format(hook=hook, hookpy=hookpy,
                                   date=util.date())
    with open(hook_file, 'w') as hookfp:
        hookfp.write(content)
    exec_cmd('chmod +x %s' % hook_file, True)


def make_acl():
    """Returns a git acl with the promus master as the only admin.
    This dictionary needs to be passed to other functions so that it
    may be updated with the information in the repositories acls."""
    acl = dict()
    acl['admin'] = [config('user.email')]
    acl['user'] = [config('user.email')]
    acl['path'] = list()
    acl['name'] = list()
    return acl


def parse_acl(aclstring):
    """Return acl dictionary. The format of the aclstring is as
    follows:

        admin: user1
        user: user2, user3, user4
        path: dir1, dir2 | !deny, user3, user4
        name: file1 | !allow, user2

    Everyone will have access to the files in the repository. If more
    control is needed we can deny access to some paths by listing the
    paths. Some files are only accessible to the admin but the admin
    may provide access to other users by listing the path (relative
    to the git repository) and using the keyword !allow. """
    acl = make_acl()
    line_num = 0
    for line in aclstring.split('\n'):
        line = line.strip()
        line_num += 1
        if line == '' or line[0] == '#':
            continue
        try:
            key, val = line.split(':')
            key = key.strip().lower()
        except ValueError:
            err_msg = "wrong number of ':' in line %d" % line_num
            raise ACLException(err_msg)
        if key in ['admin', 'user']:
            acl[key].extend(util.split_at(',', val))
        elif key in ['path', 'name']:
            try:
                tmp = val.split('|')
                files = util.split_at(',', tmp[0])
                users = util.split_at(',', tmp[1])
                acl[key].extend([files, users])
            except IndexError:
                err_msg = "'|' not found in line %d" % line_num
                raise ACLException(err_msg)
        else:
            err_msg = "wrong keyword in line %d" % line_num
            raise ACLException(err_msg)
    acl['admin'] = list(set(acl['admin']))
    acl['user'] = list(set(acl['user']+acl['admin']))
    return acl


def check_acl(aclfile):
    """Attempts to read the acl file to see if it contains any
    errors. """
    try:
        aclfile = open(aclfile, 'r').read()
    except IOError:
        raise NoACLException("acl not found: '%s'" % aclfile)
    return parse_acl(aclfile)


def read_acl(git_dir=None):
    """Read acl from the git repository."""
    if git_dir:
        cmd = 'cd %s; git show HEAD:.acl' % git_dir
    else:
        cmd = 'git show HEAD:.acl'
    aclfile, err, _ = exec_cmd(cmd)
    if err:
        raise NoACLException(err[:-1])
    return parse_acl(aclfile)


def parse_profile(profilestring):
    """Return profile dictionary. The format of the profilestring is
    as follows:

        email: user@domain.com
        notify: [all/false/track]
        track-files: pattern1, pattern2, ...

    The track-files keyword will only be relevant if notify is set to
    `track`. This tells promus to send a notification to the
    specified email address if one of the modified files matches a
    pattern. Only one keyword and options per line. You may use
    several track-files keywords. """
    profile = dict()
    profile['email'] = ''
    profile['notify'] = 'false'
    profile['track-files'] = list()
    line_num = 0
    for line in profilestring.split('\n'):
        line_num += 1
        if line.strip() == '' or line[0] == '#':
            continue
        try:
            key, val = line.split(':')
            key = key.strip().lower()
        except ValueError:
            return "wrong number of ':' in line %d" % line_num
        if key in 'email':
            profile[key] = val.strip()
        elif key in ['notify']:
            val = val.strip().lower()
            if val in ['all', 'false', 'track']:
                profile[key] = val
            else:
                return "Notify options allowed: all/false/track"
        elif key == 'track-files':
            profile[key].extend(util.split_at(',', val))
        elif line.strip() != '':
            return "wrong keyword in line %d" % line_num
    return profile


def check_profile(profile_file):
    "Attempts to read the acl file to see if it contains any errors. "
    try:
        profile = open(profile_file, 'r').read()
    except IOError:
        return "no such file: '%s'" % profile_file
    return parse_profile(profile)


def read_profile(user, git_dir=None):
    "Read profile from the git repository."
    if git_dir:
        cmd = 'cd %s; git show HEAD:.%s.profile' % (git_dir, user)
    else:
        cmd = 'git show HEAD:.%s.profile' % user
    profile, err, _ = exec_cmd(cmd, False)
    if err:
        return "while executing `git show HEAD:.%s.profile`: %s" % (user,
                                                                    err[:-1])
    return parse_profile(profile)


def file_in_path(file_name, paths):
    "Given a list of paths it checks if the file is in one of the paths."
    for path in paths:
        if file_name.startswith(path):
            return True
    return False


def file_match(file_name, names):
    """Checks the name of the file matches anything in the list of
    names. """
    fname = pth.basename(file_name)
    for name in names:
        if fnmatch(fname, name):
            return True
    return False


def load_repos():
    """Obtain the cloned git repositories. """
    try:
        file_obj = open(pth.expanduser('~/.promus/repos'), 'r')
    except IOError:
        return dict()
    try:
        repos = json.load(file_obj)
    except ValueError:
        return dict()
    file_obj.close()
    return repos


def dump_repos(repos):
    """Store the git repositories. """
    with open(pth.expanduser('~/.promus/repos'), 'w') as fp_:
        json.dump(
            repos,
            fp_,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
