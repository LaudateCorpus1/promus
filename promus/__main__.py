""" Command line use of promus

To run promus from the command line do the following:

    python -m promus [-h] subcommand

Use the option --help for more information.

"""

import argparse
import textwrap
import promus
import promus.util as util
import promus.git as git
import promus.paster as paster
import promus.unison as unison
import promus.tex as tex
from promus.__version__ import VERSION

def parse_options():
    "Interpret the command line options. "
    desc = """
promus is a remote manager which executes `git` and `unison` commands
on behalf of a user who has been given authorization via an ssh
public key.
"""
    ver = "promus %s" % VERSION
    epi = """
more info:
  http://math.uh.edu/~jmlopez/promus/

version: 
  %s

""" % VERSION
    argp = argparse.ArgumentParser(
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description=textwrap.dedent(desc),
                    version=ver, epilog=textwrap.dedent(epi))
    subp = argp.add_subparsers(title='subcommands', 
                               help='additional help',
                               dest='parser_name')

    tmpp = subp.add_parser('init', 
                           help='create a base repository (the hub)')
    tmpp.add_argument('repo', type=str, help='name of repository')

    tmpp = subp.add_parser('clone', help='clone a repository')
    tmpp.add_argument('repo', type=str, help='path to repository')

    tmpp = subp.add_parser('send-request', 
                            help='request collaborator to connect')
    tmpp.add_argument('email', type=str, help="collaborator's email")
    tmpp.add_argument('name', type=str, help="collaborator's name")

    tmpp = subp.add_parser('setup', help='adjust settings')
    tmpp = subp.add_parser('test', help='test server')

    tmpp = subp.add_parser('sync', 
                           help='synchronize untracked files with unison')
    tmpp = subp.add_parser('show', 
                           help='{keys, users}')
    tmpp.add_argument('info', type=str, help='info to be displayed')

    tmpp = subp.add_parser('connect', 
                           help='make a passworless ssh connection')
    tmpp.add_argument('host', type=str, help='the host to connect to')
    tmpp.add_argument('alias', type=str, help='host alias')
    
    tmpp = subp.add_parser('add-host', 
                           help='accept the host request')
    tmpp.add_argument('host', type=str, help='the host to connect to')
    
    tmpp = subp.add_parser('add-user', 
                           help='add user (automated)')
    tmpp.add_argument('email', type=str, help='the user email')
    
    tmpp = subp.add_parser('greet', 
                           help='attend the user')
    tmpp.add_argument('user', type=str, help='user info')
    
    tmpp = subp.add_parser('invite', 
                           help='invite user to collaborate')
    tmpp.add_argument('user', type=str, help='user name')
    
    tmpp = subp.add_parser('latexdiff', 
                           help='generate the tex file with differences')
    tmpp.add_argument('file', type=str, help='file to compare. ')
    
    tmpp = subp.add_parser('paste', 
                           help='pastes a template')
    tmpp.add_argument('template', type=str, help='template to paste. ')
    return argp.parse_args()


def run(prs):
    """Run promus from the command line. """
    arg = parse_options()
    if arg.parser_name == 'sync':
        unison.sync(prs)
    if arg.parser_name == 'init':
        git.init(prs, arg.repo)
    if arg.parser_name == 'clone':
        git.clone(prs, arg.repo)
    if arg.parser_name == 'setup':
        promus.setup(prs)
    if arg.parser_name == 'show':
        promus.show(prs, arg.info)
    if arg.parser_name == 'connect':
        promus.connect(prs, arg.host, arg.alias)
    if arg.parser_name == 'test':
        promus.server_test(prs)
    if arg.parser_name == 'send-request':
        promus.send_request(prs, arg.email, arg.name)
    if arg.parser_name == 'add-host':
        prs.add_host(arg.host)
    if arg.parser_name == 'add-user':
        prs.add_user(arg.email)
    if arg.parser_name == 'greet':
        guest, guest_name = arg.user.split(',')
        prs.greet(guest, guest_name)
    if arg.parser_name == 'latexdiff':
        tex.diff(prs, arg.file)
    if arg.parser_name == 'paste':
        paster.paste(prs, arg.template)
    if arg.parser_name == 'invite':
        prs.invite(arg.user)
    print 'Usage: promus [options]\n'
    print 'For a list of options, type "promus --help"'


if __name__ == '__main__':
    PRS = promus.Promus(__file__)
    run(PRS)
