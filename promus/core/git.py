"""Git utility"""
from __future__ import print_function
import os
import sys
from os.path import dirname, exists, split, basename
from fnmatch import fnmatch
from promus.command import exec_cmd, error
PC = sys.modules['promus.core']


def config(entry, val=None, global_setting=True):
    """Call `git config --global` when `global_setting` is set to
    True, otherwise call `git config` to set or get an entry. """
    cmd = 'git config '
    if global_setting:
        cmd += '--global '
    if val:
        exec_cmd('%s %s "%s"' % (cmd, entry, val))
    else:
        val, _, _ = exec_cmd('%s %s' % (cmd, entry))
    return val.strip()


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
    return PC.strip(out)


def local_path():
    "Return the path to directory containing the `.git` directory. "
    out, _, _ = exec_cmd('git rev-parse --show-toplevel')
    return PC.strip(out)


def remote_path():
    "Return the path of the remote repository. "
    out, _, _ = exec_cmd('git config --get remote.origin.url')
    return PC.strip(out)


def init(repo, directory=None):
    """Create a bare git repository and create the `post-receive` and
    `update` hook. You may have to modify these two hooks depending
    on how you want to treat the repository. """
    if not repo.endswith('.git'):
        repo += '.git'
    if directory is None:
        directory = '%s/git' % os.environ['HOME']
    PC.make_dir(directory)
    fullpath = '%s/%s' % (directory, repo)
    if os.path.exists(fullpath):
        error("INIT-ERROR>> Existing repository: '%s'\n" % fullpath)
    exec_cmd("git init --bare %s" % fullpath, True)
    hooks = ['post-receive', 'update']
    for hook in hooks:
        path = '%s/hooks' % fullpath
        make_hook(hook, path)
    sys.stdout.write("INIT>> '%s' was created...\n" % fullpath)


HOOK_TEMPLATE = '''#!/usr/bin/env python
"""{hook} hook generated on {date}"""
import promus.core as prc
import promus.hooks.{hookpy} as hook

if __name__ == "__main__":
    PRS = prc.Promus()
    hook.run(PRS)
    PRS.dismiss("{hook}>> done...", 0)

'''


def make_hook(hook, path):
    "Creates the specified hook. "
    hook_file = "%s/%s" % (path, hook)
    if exists(hook_file):
        cmd = "mv %s %s.%s" % (hook_file, hook_file, PC.date(True))
        exec_cmd(cmd, True)
    hookpy = hook.replace('-', '_')
    content = HOOK_TEMPLATE.format(hook=hook, hookpy=hookpy,
                                   date=PC.date())
    with open(hook_file, 'w') as hookfp:
        hookfp.write(content)
    exec_cmd('chmod +x %s' % hook_file, True)


def parse_dir(string):
    "Return two lists, one with directories and one with users. "
    tmp = string.split('|')
    return [PC.parse_list(tmp[0]), PC.parse_list(tmp[1])]


def parse_acl(aclstring):
    """Return acl dictionary. The format of the aclstring is as
    follows:

        admin: user1
        user: user2, user3, user4
        path: dir1, dir2 | !deny, user3, user4
        name: file1 | !allow, user2
        rsync: user2, user4

    Everyone will have access to the files in the repository. If more
    control is needed we can deny access to some paths by listing the
    paths. Some files are only accessible to the admin but the admin
    may provide access to other users by listing the path (relative
    to the git repository) and using the keyword !allow. The rsync
    keyword lists the users which will get synchronized files using
    rsync. That is, the user will not be able to modify the files.
    They will only get the lastest copy of them. """
    acl = dict()
    acl['admin'] = list()
    acl['user'] = list()
    acl['path'] = list()
    acl['name'] = list()
    acl['rsync'] = list()
    line_num = 0
    for line in aclstring.split('\n'):
        line_num += 1
        if line.strip() == '' or line[0] == '#':
            continue
        try:
            key, val = line.split(':')
            key = key.strip().lower()
        except ValueError:
            return "wrong number of ':' in line %d" % line_num
        if key in ['admin', 'user']:
            acl[key].extend(PC.parse_list(val))
        elif key in ['path', 'name']:
            try:
                acl[key].extend(parse_dir(val))
            except IndexError:
                return "'|' not found in line %d" % line_num
        elif key == 'rsync':
            acl[key].extend(PC.parse_list(val))
        elif line.strip() != '':
            return "wrong keyword in line %d" % line_num
    acl['user'] = list(set(acl['user']+acl['admin']))
    return acl


def check_acl(aclfile):
    "Attempts to read the acl file to see if it contains any errors. "
    try:
        aclfile = open(aclfile, 'r').read()
    except IOError:
        return "no such file: '%s'" % aclfile
    return parse_acl(aclfile)


def read_acl(git_dir=None):
    "Read acl from the git repository."
    if git_dir:
        cmd = 'cd %s; git show HEAD:.acl' % git_dir
    else:
        cmd = 'git show HEAD:.acl'
    aclfile, err, _ = exec_cmd(cmd, False)
    if err:
        return "while executing `git show HEAD:.acl`: %s" % err[:-1]
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
            profile[key].extend(PC.parse_list(val))
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


def has_access(user, users):
    """A list of users should look as follows: ['!deny', 'user1',
    'user2'] This means that user1 and user2 have deny access. If we
    have something longer such as ['!deny', 'user1', '!allow',
    'user2'] then user2 has access but user1 does not have access. If
    no keywords are found then it returns None if the user is in the
    list. """
    if user not in users:
        return None
    rusers = users[::-1]
    try:
        action = next(x[1] for x in enumerate(rusers) if x[1][0] == '!')
    except StopIteration:
        return None
    if action == '!allow':
        return True
    if action == '!deny':
        return False
    return False


def file_match(file_name, names):
    """Checks the name of the file matches anything in the list of
    names. """
    fname = basename(file_name)
    for name in names:
        if fnmatch(fname, name):
            return True
    return False


def clone(repo):
    "Clone a repository. "
    out, err, stat = exec_cmd("git clone %s" % repo)
    sys.stdout.write(out)
    if stat != 0:
        error(err)
    if repo[-1] == '/':
        tmp = split(repo[0:-1])
    else:
        tmp = split(repo)
    repo = tmp[1].split('.')[0]
    if not exists("%s/.acl" % repo):
        admin_setup(repo)
    else:
        user_setup(repo)
    if os.uname()[0] == 'Darwin':
        exec_cmd('open -a /Applications/GitHub.app "%s"' % repo, True)
    sys.stderr.write("CLONE>> Repository '%s' has been cloned ...\n" % repo)


def admin_setup(repo):
    "Set the acl list and create the hooks. "
    print("Setting up empty repository...")
    print("creating README.md")
    master = os.environ['USER']
    email = config('user.email').strip()
    exec_cmd("touch %s/README.rst" % repo, True)

    print("creating .acl")
    with open('%s/.acl' % repo, 'w') as tmpf:
        tmpf.write('admin : %s\n' % master)
        tmpf.write('user  : \n')

    print("creating .%s.profile" % email)
    with open('%s/.%s.profile' % (repo, email), 'w') as tmpf:
        tmpf.write('email: %s\n' % email)
        tmpf.write('notify: all\n')
        tmpf.write('track-files: \n')

    print("creating .description")
    with open('%s/.description' % repo, 'w') as tmpf:
        tmpf.write('%s description goes here\n' % repo)
    try:
        os.remove('%s/.git/description' % repo)
    except OSError:
        pass
    exec_cmd('ln -s ../.description %s/.git/description' % repo, True)

    print("creating .bashrc")
    with open('%s/.bashrc' % repo, 'w') as tmpf:
        tmpf.write('# Bash commands related to %s\n' % repo)

    print("creating hooks:")
    hooks = ['commit-msg', 'post-checkout', 'post-commit', 'post-merge',
             'pre-commit', 'pre-rebase',
             'prepare-commit-msg']
    for hook in hooks:
        print("  %s" % hook)
        path = '%s/.git/hooks' % repo
        make_hook(hook, path)

    print("copying .gitignore\n")
    tmp = dirname(__file__)
    exec_cmd('cp %s/../paster/gitignore.txt %s/.gitignore' % (tmp, repo), True)


def user_setup(repo):
    "Create the user profile"
    print("Setting up repository...")
    print("linking .description...")
    email = config('user.email').strip()
    try:
        os.remove('%s/.git/description' % repo)
    except OSError:
        pass
    exec_cmd('ln -s ../.description %s/.git/description' % repo, True)

    user_profile = '%s/.%s.profile' % (repo, email)
    if not exists(user_profile):
        print("creating .%s.profile" % email)
        with open(user_profile, 'w') as tmpf:
            tmpf.write('email: %s\n' % email)
            tmpf.write('notify: all\n')
            tmpf.write('track-files: \n')

    print("creating hooks:")
    hooks = ['commit-msg', 'post-checkout', 'post-commit', 'post-merge',
             'pre-commit', 'pre-rebase', 'prepare-commit-msg']
    for hook in hooks:
        print("  %s" % hook)
        path = '%s/.git/hooks' % repo
        make_hook(hook, path)
