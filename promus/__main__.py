""" Command line use of promus

To run promus from the command line do the following:

    python -m promus [-h] subcommand

Use the option --help for more information.

"""

import argparse
import textwrap
from os.path import split, abspath
from glob import iglob
from promus.__version__ import VERSION
from promus.command import import_mod
try:
    import argcomplete
except ImportError:
    pass


def parse_options(mod):
    """Interpret the command line inputs and options. """
    desc = """
promus is a remote manager designed to create and manage `git`
repositories in a remote server without the need of administrator
privileges.

use the help option with a command for more information on what
promus can do.

"""
    ver = "promus %s" % VERSION
    epi = """
more info:
  http://promus.readthedocs.org

version:
  promus %s

""" % VERSION
    raw = argparse.RawDescriptionHelpFormatter
    argp = argparse.ArgumentParser(formatter_class=raw,
                                   description=textwrap.dedent(desc),
                                   epilog=textwrap.dedent(epi))
    argp.add_argument('-v', '--version', action='version', version=ver)
    subp = argp.add_subparsers(title='subcommands',
                               dest='parser_name',
                               help='additional help',
                               metavar="<command>")
    names = sorted(mod.keys())
    for name in names:
        mod[name].add_parser(subp, raw)
    try:
        argcomplete.autocomplete(argp)
    except NameError:
        pass
    return argp.parse_args()


def run():
    """Run promus from the command line. """
    mod = dict()
    rootpath = split(abspath(__file__))[0]

    mod_names = [name for name in iglob('%s/command/*.py' % rootpath)]
    for name in mod_names:
        tmp_name = split(name)[1][:-3]
        tmp_mod = import_mod('promus.command.%s' % tmp_name)
        if hasattr(tmp_mod, 'add_parser'):
            mod[tmp_name] = tmp_mod

    arg = parse_options(mod)
    mod[arg.parser_name].run(arg)

if __name__ == '__main__':
    run()
