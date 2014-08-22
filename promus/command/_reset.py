"""_RESET

This is an axilary function to fix the old repositories created with
the beta version of promus.

"""

import textwrap
import promus.core as prc


DESC = """
Reset the git hooks. Note that this version does not create a backup
of the current hooks. Also you must be in the git repository.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('_reset',
                           help='reset git hooks',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('--bare', action='store_true',
                      help="Use this option for bare repositories")


def reset_hooks():
    """Command to rest hooks in a repository. """
    print("resetting hooks:")
    hooks = ['commit-msg', 'post-checkout', 'post-commit', 'post-merge',
             'pre-commit', 'pre-rebase',
             'prepare-commit-msg']
    for hook in hooks:
        print("  %s" % hook)
        path = './.git/hooks'
        prc.make_hook(hook, path)


def reset_hooks_bare():
    """Command to reset hooks in a bare repository. """
    print("resetting hooks in bare repository:")
    hooks = ['post-receive', 'update']
    for hook in hooks:
        print("  %s" % hook)
        path = './hooks'
        prc.make_hook(hook, path)


def run(arg):
    """Run command. """
    if arg.bare:
        reset_hooks_bare()
    else:
        reset_hooks()
