"""
clone an existing repository. To see which repositories you can clone
try the `search` command.

"""
import sys
import textwrap
import os.path as pth
from promus.command import error, disp, exec_cmd
from promus.core import git


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('clone',
                           help='clone an existing repository',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('repo', type=str,
                      help='the repository to clone')


def admin_setup(repo):
    """Set the acl list and create the hooks. """
    disp("  - creating README.rst\n")
    exec_cmd("touch {0}/README.rst".format(repo), True)
    disp("  - creating .acl\n")
    with open(pth.join(repo, '.acl'), 'w') as tmpf:
        tmpf.write('admin : {0}\n'.format(git.config('user.email')))
        tmpf.write('user  : \n')
    disp("  - copying .gitignore\n")
    cmd = 'cp {0}/../paster/gitignore.txt {1}/.gitignore'
    exec_cmd(cmd.format(pth.dirname(__file__), repo), True)


def user_setup(repo):
    """Create the user profile. """
    email = git.config('user.email')
    user_profile = '{0}/.{1}.profile'.format(repo, email)
    if not pth.exists(user_profile):
        disp("  - creating user profile\n")
        with open(user_profile, 'w') as tmpf:
            tmpf.write('email: %s\n' % email)
            tmpf.write('notify: all\n')
            tmpf.write('track-files: \n')
    disp("  - creating hooks\n")
    hooks = [
        'commit-msg', 'post-checkout', 'post-commit', 'post-merge',
        'pre-commit', 'pre-rebase', 'prepare-commit-msg'
    ]
    for hook in hooks:
        disp("    * %s\n" % hook)
        git.make_hook(hook, '{0}/.git/hooks'.format(repo))


def store_repo(remote_repo, cloned_repo):
    """Keep track of the cloned repositories. """
    repos = git.load_repos()
    if remote_repo not in repos:
        repos[remote_repo] = [cloned_repo]
    else:
        if cloned_repo not in repos[remote_repo]:
            repos[remote_repo].append(cloned_repo)
        updated = [x for x in repos[remote_repo] if pth.exists(x)]
        repos[remote_repo] = updated
    git.dump_repos(repos)


def run(arg):
    """Run command. """
    repo = arg.repo
    if repo.endswith('/'):
        repo = repo[:-1]
    if not repo.endswith('.git'):
        repo += '.git'
    cmd = 'git clone {repo}'.format(repo=repo)
    _, _, exit_code = exec_cmd(cmd, True)
    if exit_code != 0:
        error('ERROR: see above\n')
    remote_repo = repo
    tmp = pth.split(repo)
    repo = tmp[1].split('.')[0]
    if not pth.exists(pth.join(repo, '.acl')):
        admin_setup(repo)
    user_setup(repo)
    if sys.platform in ['Darwin', 'darwin']:
        exec_cmd('open -a /Applications/GitHub.app "%s"' % repo, True)
    disp("'{repo}' has been cloned\n".format(repo=repo))
    store_repo(remote_repo, pth.abspath(repo))
