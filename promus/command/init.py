"""
create a new git repository in the directory `~/git`. You may create
a new repository in another directory by providing the option `--dir`.

NOTE: this action creates the `post-receive` and `update` hooks.

"""
import textwrap
import os.path as pth
from promus.core import util, git
from promus.command import error, disp, exec_cmd


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('init',
                           help='create a bare repository (the hub)',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('repo', type=str,
                      help='the repository name')
    tmpp.add_argument('-d', '--dir', type=str, default=None,
                      help='directory where to store the respository')


def run(arg):
    """Run command. """
    repo = arg.repo
    directory = arg.dir
    if not repo.endswith('.git'):
        repo += '.git'
    if directory is None:
        directory = pth.expanduser('~/git')
    util.make_dir(directory)
    full_path = pth.join(directory, repo)
    if pth.exists(full_path):
        error("ERROR: '%s' is an existing repository.\n" % full_path)
    exec_cmd("git init --bare %s" % full_path, True)
    hooks = ['post-receive', 'update']
    for hook in hooks:
        path = pth.join(full_path, 'hooks')
        git.make_hook(hook, path)
    disp("'%s' was created.\n" % full_path)
