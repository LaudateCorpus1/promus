"""
synchronize two directories in a similar fashion as DropBox using
rsync as the main process to transfer files.

add entry:
    $ promus sync local_dir remote_dir

add entry with alias:
    $ promus sync local_dir remote_dir alias

list entries:
    $ promus sync

sync entry:
    $ promus sync index/alias

"""
import textwrap
import argparse
import promus.core.sync as sync
from promus.command import disp


# pylint: disable=too-few-public-methods
class ArgumentAction(argparse.Action):
    """Derived argparse Action class to use when registering two
    directories. """
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 3:
            disp('usage: promus [-h] [-v] <command> ...\n')
            disp('promus: error: unrecognized arguments: %s\n' % (
                ' '.join(values[3:])
            ))
            exit(2)
        namespace.display = False
        namespace.index = None
        namespace.register = False
        if len(values) == 3:
            namespace.local = values[0]
            namespace.remote = values[1]
            namespace.alias = values[2]
            namespace.register = True
        elif len(values) == 2:
            namespace.local = values[0]
            namespace.remote = values[1]
            namespace.alias = ''
            namespace.register = True
        elif len(values) == 1:
            namespace.index = values[0]
        else:
            namespace.display = True


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('sync', help='sync directories',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('arg', type=str, nargs='*',
                      help='arguments (at most 3)',
                      action=ArgumentAction)
    tmpp.add_argument('--set-alias', metavar='ALIAS',
                      dest='mod_alias', default=None,
                      help="modify the alias of an entry")
    tmpp.add_argument('--remove', action='store_true',
                      help="remove an entry")
    tmpp.add_argument('--reset', action='store_true',
                      help="reset last sync date")


def run(arg):
    """Run command. """
    if arg.register:
        sync.register(arg.local, arg.remote, arg.alias)
    elif arg.mod_alias is not None:
        sync.set_alias(arg.index, arg.mod_alias)
    elif arg.remove:
        sync.unregister(arg.index)
    elif arg.reset:
        sync.reset_date(arg.index)
    elif arg.index:
        sync.sync_entry(arg.index)
    elif arg.display:
        config = sync.load_config()
        for num, _ in enumerate(config):
            sync.print_entry(config, num)
        if len(config) == 0:
            sync.c_warn('No entries to show. see "promus sync -h"')