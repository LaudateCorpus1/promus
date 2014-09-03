"""
to be able to collaborate first you need to let your collaborators be
able to connect to your account. You may do this by sending a request.

    promus send request email@hostname 'First Last'

"""
import os
import socket
import textwrap
from promus import send_mail
from promus.core import git, ssh
from promus.command import disp


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('send', help='send a collaboration request',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('type', metavar='TYPE', type=str,
                      choices=['request'],
                      help='One of the following: request')
    tmpp.add_argument('email', type=str,
                      help="collaborators email")
    tmpp.add_argument('name', type=str, nargs='?',
                      help="collaborators name")

REQUEST_TXT = """Hello {name},

This email has been generated on behalf of {master} to request for
your public key. This will give access to future repositories hosted
by {master} so that you may work as a team.

To accomplish this, you will need to have promus installed. If you do
not have it please visit the following page and take a moment to
learn the basics of promus.

    http://promus.readthedocs.org

Once you have promus you need to download the attached file. Then
navigate to the directory where you downloaded the file and type:

    promus add host {masteruser}@{host}

You and {master} will recieve a notification shortly after running
the command verifying that the connection was successful.

- Promus

"""
REQUEST_HTML = """<p>Hello <strong>{name}</strong>,</p>
<p>This email has been generated on behalf of <em>{master}</em> to
request for your public key. This will give access to future
repositories hosted by <em>{master}</em> so that you may work as a
team.</p>
<p>To accomplish this, you will need to have promus installed. If you
do not have it please visit the following page and take a moment to
learn the basics of promus.</p>
<pre><code>    <a
href="http://promus.readthedocs.org">http://promus.readthedocs.org</a>
</code></pre>
<p>Once you have promus you need to download the attached file. Then
navigate to the directory where you downloaded the file and type:</p>
<pre><code>    promus add host {masteruser}@{host}
</code></pre>
<p>You and {master} will recieve a notification shortly after
running the command verifying that the connection was successful.</p>
<p>
<strong>- Promus</strong>
</p>
"""


def send_request(arg):
    """Sends an email to request for a public key. """
    home = os.environ['HOME']
    host = socket.gethostname()
    master = os.environ['USER']
    key = ssh.make_key('%s/.promus/%s@%s' % (home, master, host))
    users, pending, unknown = ssh.read_authorized_keys()
    key_type, ssh_key = ssh.get_public_key(key).split()
    pending[ssh_key] = [arg.email, key_type, arg.email]
    ssh.write_authorized_keys(users, pending, unknown)
    if arg.name is None:
        name = 'future collaborator'
    else:
        name = arg.name
    mastername = git.config('user.name')
    disp('sending request ... ')
    send_mail([arg.email],
              'Collaboration request from %s' % mastername,
              REQUEST_TXT.format(name=name, masteruser=master,
                                 master=mastername, host=host),
              REQUEST_HTML.format(name=name, masteruser=master,
                                  master=mastername, host=host),
              [key])
    os.remove(key)
    disp('done\n')


def run(arg):
    """Run command. """
    func = {
        'request': send_request,
    }
    func[arg.type](arg)
