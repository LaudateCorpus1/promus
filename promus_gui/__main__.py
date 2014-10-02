""" Graphical User Interface

To run the gui do the following in the command line:

    python -m promus_gui [-h] [-p]

Use the option --help for more information.

"""
import argparse
import textwrap
import webbrowser
from flask import Flask
from promus.__version__ import VERSION
APP = Flask(__name__)


def parse_options():
    """Interpret the command line inputs and options. """
    desc = """
this is the graphical user interface for promus. If you are having
trouble initializing the server you may use the options `-p` to
select the port or `-n` to specify the host name.
"""
    ver = "promus-gui %s" % VERSION
    epi = """
more info:
  http://promus.readthedocs.org

version:
  promus-gui %s

""" % VERSION
    raw = argparse.RawDescriptionHelpFormatter
    argp = argparse.ArgumentParser(formatter_class=raw,
                                   description=textwrap.dedent(desc),
                                   epilog=textwrap.dedent(epi))
    argp.add_argument('-v', '--version', action='version', version=ver)
    argp.add_argument('-p', type=int, metavar="PORT",
                      help="port number", default=5000)
    argp.add_argument('-n', type=str, metavar="HOSTNAME",
                      help="host name", default="localhost")
    return argp.parse_args()


@APP.route("/")
def hello():
    """Testing function. """
    return "Hello World!"


def run():
    """Run promus-gui from the command line. """
    arg = parse_options()
    port = arg.p
    host = arg.n
    webbrowser.open_new("http://%s:%d" % (host, port))
    APP.run(host=host, port=port)


if __name__ == "__main__":
    run()
