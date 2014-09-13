"""
execute a python function on a host. The following commands are
equivalent:

    promus exec-on <host> <func> <args>

    ssh <host> __PYFUNC__ <func> <args>

"""
import textwrap
import argparse
from promus.command import exec_cmd


# pylint: disable=too-few-public-methods
class DisplayDocAction(argparse.Action):
    """Display the documentation of a remote python function. """
    def __call__(self, parser, namespace, values, option_string=None):
        host = namespace.host
        func = namespace.pyfunc
        cmd = 'ssh {host} __DOC__ {func}'.format(host=host, func=func)
        _, _, code = exec_cmd(cmd, True)
        exit(code)


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('exec-on',
                           help='execute a command on a host',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('host', type=str,
                      help="host name")
    tmpp.add_argument('pyfunc', type=str,
                      help="command to execute")
    tmpp.add_argument('args', type=str, nargs="*",
                      help="arguments to python function")
    tmpp.add_argument('-d', '--doc', action=DisplayDocAction,
                      nargs=0,
                      help="display documentation and exit")


def run(arg):
    """Run command. """
    cmd = 'ssh {host} __PYFUNC__ {func} {args}'
    args = ' '.join(arg.args).replace('"', '\\"')
    args = args.replace("'", "\\'")
    cmd = cmd.format(
        host=arg.host,
        func=arg.pyfunc,
        args=args
    )
    exec_cmd(cmd, True)
