"""A Remote Manager"""

import re
import sys
import socket
from os import environ
from os.path import realpath, exists, expanduser, basename
from subprocess import Popen, PIPE
from smtplib import SMTP_SSL as SMTP
#from email.mime.text import MIMEText
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import Encoders
import site
import getpass
import promus.util as util
import promus.git as git
import promus.ssh as ssh

__all__ = ['Promus']

USERBASE = site.getuserbase()
PREFIX = sys.prefix
environ['PATH'] = '%s/bin:%s/bin:%s' % (USERBASE, PREFIX, environ['PATH'])


def gconfig_git(prompt, entry, default=''):
    """Ask user to set value for a git entry. """
    val = git.gconfig(entry)
    if val == '':
        val = default
    val = util.user_input(prompt, val.strip())
    return git.gconfig(entry, val)


def setup(prs):
    """Enter wizard mode to make sure all settings are correct. """
    git.gconfig('host.name', socket.gethostname())
    gconfig_git("Hostname alias", 'host.alias')
    gconfig_git("Full name", 'user.name')
    gconfig_git("E-mail address", 'user.email')
    email = gconfig_git("Host e-mail", 'host.email')
    idkey, _ = ssh.get_keys(prs)
    util.save_password(idkey, getpass.getpass())
    host_email = email.split(':')[0]
    [username, server] = email.split('@')
    git.gconfig('host.email', host_email)
    git.gconfig('host.username', username)
    git.gconfig('host.smtpserver', 'smtp.%s' % server)
    prs.dismiss("SETUP>> complete ...", 0)


def show(prs, info):
    """Display info. """
    if info == 'keys':
        idkey, gitkey = ssh.get_keys(prs)
        idkey = ssh.get_public_key(idkey)
        print '# ID_RSA:'
        print '%s %s@%s - %s' % (idkey, prs.master, prs.host, prs.alias)
        gitkey = ssh.get_public_key(gitkey)
        print '# GIT_KEY:'
        print '%s %s@%s - %s' % (gitkey, prs.master, prs.host, prs.alias)
    elif info == 'users':
        users, unknown = ssh.read_authorized_keys(prs)
        print '  '
        for user, val in users.items():
            print '  %s: %s' % (user, ', '.join([x['host'] for x in val]))
        print '  '
        if unknown:
            msg = 'There are [%d] unknown entries in ~/.ssh/authorized_keys:'
            print msg % len(unknown)
    else:
        prs.dismiss("SHOW-ERROR>> %s is not a valid keyword ..." % info, 1)
    prs.dismiss("SHOW>> complete ...", 0)


def connect(prs, host, alias):
    """Create a passworless ssh connection. """
    tmp = host.split('@')
    if len(tmp) == 2:
        user = tmp[0]
        host = tmp[1]
    else:
        user = prs.master
        host = tmp[0]
    idkey, _ = ssh.get_keys(prs)
    idkey = ssh.get_public_key(idkey)
    key = idkey.split()[1]
    append_cmd = "echo \"%s %s@%s\n\" >> .ssh/authorized_keys"
    append_cmd = append_cmd % (idkey, prs.master, prs.host)
    cmd = "ssh %s@%s 'mkdir -p ~/.ssh; touch ~/.ssh/authorized_keys; " \
          "if grep -q %s .ssh/authorized_keys; then " \
          "echo \"[REMOTE]: Connection has been previously established\"; " \
          "else %s; fi; chmod 700 ~/.ssh; chmod 700 ~/.ssh/authorized_keys'"
    cmd = cmd % (user, host, key, append_cmd)
    util.exec_cmd(cmd, True)
    if alias:
        config = ssh.read_config(prs)
        found = False
        for entry in config:
            if alias in entry.split():
                found = True
                prs.log('Alias already in use:  `Host %s`' % entry)
                break
        if not found:
            entry = '%s %s' % (alias, host)
            config[entry] = dict()
            config[entry]['HostName'] = host
            config[entry]['User'] = user
            ssh.write_config(prs, config)
        prs.log('You may connect to %s using: `ssh %s`' % (host, alias))
    prs.dismiss("CONNECT>> complete ...", 0)


def send_request(prs, email, name):
    """Send a request to a collaborator to connect to your server. """
    key = ssh.make_key('%s/.promus/%s.key' % (prs.home, email))
    tmpkey = '%s/.promus/%s@%s' % (prs.home, prs.master, prs.host)
    util.exec_cmd('cp %s %s' % (key, tmpkey), True)
    users, unknown = ssh.read_authorized_keys(prs)

    found = False
    for entry in unknown:
        if email.replace('@', ':') in entry:
            found = True
            break
    if not found:
        cmd = 'command="python -m promus add-user %s"' % email
        entry = '%s %s %s' % (cmd, ssh.get_public_key(key), email.replace('@', ':'))
        unknown.append(entry)
    ssh.write_authorized_keys(prs, users, unknown)
    subject = 'Connection request from %s' % git.gconfig('user.name')
    text = """Greetings %s,
    
    %s would like to give you access to his repositories. To do so you
    must first provide him with a public key of your own. 
    
    Please download the attached file. If you do not have promus 
    you may install it by following the instructions in this page:
    
        http://math.uh.edu/~jmlopez/promus/
    
    If you already have promus then navigate to the directory where
    you downloaded the file (in your terminal) and type:
    
        promus add-host %s@%s
    
    You should recieve a notification shortly after running the 
    command informing you and %s that the registration was completed.
    
        - Promus
    
    """ % (name, prs.master_name, prs.master, prs.host, prs.master_name)
    html = """<h3>Greetings %s,</h3>
    
    <p>
    %s would like to give you access to his repositories. To do so you
    must first provide him one of your public keys.
    </p>
    
    <p>
    Please download the attached file. If you do not have promus 
    you may install it by following the instructions in this page:
    </p>
    
    <pre><code>
    <a href="http://math.uh.edu/~jmlopez/promus/">http://math.uh.edu/~jmlopez/promus/</a></code></pre>
    
    <p>
    If you already have promus then navigate to the directory where
    you downloaded the file (in your terminal) and type:
    </p>
    
    <pre><code>
    promus add-host %s@%s</code></pre>
    
    <p>
    You should recieve a notification shortly after running the 
    command informing you and %s that the registration was completed.
    </p>
    
    
    <p>
    <strong>- Promus</strong>
    </p>
    """ % (name, prs.master_name, prs.master, prs.host, prs.master_name)
    send_mail(prs, [email], subject, text, html, [tmpkey])
    prs.dismiss("SEND-REQUEST>> complete ...", 0)


def send_mail(prs, send_to, subject, text, html, files=None):
    """Send an email. """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'promus@%s' % prs.host
    msg['To'] = ','.join(send_to)

    msg.attach(MIMEText(text, 'plain'))
    htmlmsg = MIMEMultipart()
    htmlmsg.attach(MIMEText(html, 'html'))

    if files is None:
        files = list()
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 
                        'attachment; filename="%s"' % basename(f))
        htmlmsg.attach(part)
    msg.attach(htmlmsg)
    server = git.gconfig('host.smtpserver')
    conn = SMTP(server)
    conn.set_debuglevel(False)
    idkey, _ = ssh.get_keys(prs)
    password = util.load_password(idkey)
    if password:
        username = git.gconfig('host.username')
        prs.log("SEND-MAIL>> login as %s to %s ..." % (username, server))
        conn.login(username, password)
    try:
        hostemail = git.gconfig('host.email')
        prs.log("SEND-MAIL>> sending to %s ..." % str(send_to))
        conn.sendmail(hostemail, send_to, msg.as_string())
    finally:
        conn.close()


def server_test(prs):
    """Check to see if email works. """
    send_to = [git.gconfig('user.email')]
    subject = 'Server Test'
    text = 'This message was generated by promus to make sure promus is ' \
           'able of sending emails. '
    send_mail(prs, send_to, subject, text, text)
    prs.dismiss("SERVER-TEST>> complete ...", 0)


# pylint: disable=R0902
class Promus(object):
    "An instance of this object manages the commands issued over ssh. "

    def __init__(self, script):
        # Host information
        self.host = socket.gethostname()
        self.alias = git.gconfig('host.alias')
        self.home = environ['HOME']
        self.master = environ['USER']
        self.master_name = git.gconfig('user.name')

        # Guest information
        self.guest = None
        self.guest_name = None
        self.cmd = None
        self.cmd_token = None
        self.cmd_name = None

        # Setting up log file
        self.path = '%s/.promus' % self.home
        util.make_dir(self.path)
        self.log_file = open('%s/promus.log' % self.path, 'a')
        script = realpath(script).replace(self.home, '~')
        self.log("INIT>> Running %s in %s" % (script, self.host))

        # Setting up functions based on command name
        self._exec = dict()
        self._exec['git-receive-pack'] = exec_git
        self._exec['git-upload-pack'] = exec_git
        self._exec['promus-find'] = promus_find
        self._exec['unison'] = exec_unison

    def log(self, msg):
        "Write a message to the log file. "
        sys.stderr.write("[PROMUS]: %s\n" % msg)
        msg = '[%s:~ %s]$ %s\n' % (util.date(True), self.guest, msg)
        self.log_file.write(msg)

    def dismiss(self, msg, status):
        """Print msg to the standard error stream (sys.stderr), as
        well as to the log file and exit with the provided status. """
        self.log(msg)
        self.log_file.close()
        exit(status)

    def execute(self, cmd_name):
        """Execute one of the commands promus is allowed to execute.
        These are defined in the init function. If a command is not
        there then the deny function will be executed instead. """
        self._exec.get(cmd_name, deny)(self)

    def exec_cmd(self, cmd, verbose=False):
        "Run a subprocess and return its output and errors. "
        self.log("EXEC>> %s" % cmd)
        if verbose:
            out = sys.stdout
            err = sys.stderr
        else:
            out = PIPE
            err = PIPE
        process = Popen(cmd, shell=True, stdout=out, stderr=err)
        out, err = process.communicate()
        if verbose:
            with open('%s/promus.last' % self.path, 'w') as tmpf:
                tmpf.write("%s\n" % self.guest)
                tmpf.write("%s\n" % self.guest_name)
                tmpf.write("%s" % self.cmd)
        return out, err, process.returncode

    def _get_cmd(self):
        "Check to see if a command was given. Exit if it is not present. "
        if 'SSH_ORIGINAL_COMMAND' not in environ:
            msg = "GET_CMD-ERROR>> SSH_ORIGINAL_COMMAND not found."
            self.dismiss(msg, 1)
        self.cmd = environ['SSH_ORIGINAL_COMMAND']
        pattern = re.compile('.*?[;&|]')
        if pattern.search(self.cmd):
            msg = "GET_CMD-ERROR>> More than one command: %s" % self.cmd
            self.dismiss(msg, 1)
        self.cmd_token = self.cmd.split()
        self.cmd_name = self.cmd_token[0]

    def attend_last(self):
        """Reads the file containing the last guest and sets the
        guest info in order to proceed writing logs with that name.
        """
        with open('%s/promus.last' % self.path, 'r') as tmpf:
            info = tmpf.read()
        self.guest, self.guest_name, self.cmd = info.split('\n')
        self.cmd_token = self.cmd.split()
        self.cmd_name = self.cmd_token[0]

    def greet(self, guest, guest_name):
        "Handle the guest request. "
        self.log("GREET>> Connected as %s" % guest)
        self.guest = guest
        self.guest_name = guest_name
        self._get_cmd()
        if self.guest == self.master:
            self.exec_cmd(self.cmd, True)
        else:
            self.execute(self.cmd_name)
        self.dismiss("GREET>> done ...", 0)
    
    def invite(self, user):
        """Invite a user to collaborate. """
        print "This command is not available yet..."
        self.dismiss("INVITE>> done ...", 0)

    def add_host(self, host):
        "Accept the host invitation. "
        util.exec_cmd("chmod 700 %s" % host, True)
        _, gitkey = ssh.get_keys(self)
        gitkey = ssh.get_public_key(gitkey)
        cmd = "ssh -i %s %s %s,%s,%s,%s,%s" % (host, host, gitkey, self.master, self.master_name, self.host, self.alias)
        util.exec_cmd(cmd, True)
        util.exec_cmd('rm %s' % host)
        config = ssh.read_config(self)
        found = False
        for entry in config:
            if host.replace('@', '-') in entry.split():
                found = True
                self.log('Existing entry: `Host %s`' % entry)
                break
        if not found:
            _, gitkey = ssh.get_keys(self)
            entry = '%s' % host.replace('@', '-')
            config[entry] = dict()
            user, host = host.split('@')
            config[entry]['HostName'] = host
            config[entry]['User'] = user
            config[entry]['IdentityFile'] = gitkey 
            ssh.write_config(self, config)
        self.dismiss("ADD-HOST>> done ...", 0)

    def add_user(self, email):
        "add user"
        info = environ['SSH_ORIGINAL_COMMAND']
        key, user, username, host, alias = info.split(',')
        
        users, unknown = ssh.read_authorized_keys(self)
        # Remove access from private key
        unknown = [entry for entry in unknown if email.replace('@', ':') not in entry]
        util.exec_cmd('rm -rf %s/.promus/%s.key' % (self.home, email), True)
        util.exec_cmd('rm -rf %s/.promus/%s.key.pub' % (self.home, email), True)
        
        info = dict()
        info['start'] = 'command="python -m promus greet \'%s,%s - %s\'"' % (user, username, alias)
        info['type'], info['key'] = key.split()
        info['type'] = info['type'][-3:]
        info['host'] = host
        if user in users:
            users[user].append(info)
        else:
            users[user] = [info]
        ssh.write_authorized_keys(self, users, unknown)
        
        subject = 'Connection successful'
        text = """Greetings %s,
    
        Your public key has been added and you may now connect to
        %s as %s using your public key. You may only run git commands
        however. Please wait for another email from %s with instructions
        on how to clone a repository.
        
          - Promus
    
        """ % (username, self.host, self.master, self.master_name)
        html = """<h3>Greetings %s,</h3>
    
        <p>
        Your public key has been added and you may now connect to
        %s as %s using your public key. You may only run git commands
        however. Please wait for another email from %s with instructions
        on how to clone a repository.
        </p>
        <p><strong>- Promus</strong></p>
        """ % (username, self.host, self.master, self.master_name)
        send_mail(self, [email, git.gconfig('host.email')], subject, text, html)
        self.dismiss("ADD-USER>> done ...", 0)

def deny(prs):
    "Promus object default action. "
    msg = "EXEC-ERROR>> Not enough permissions to run: '%s'" % prs.cmd
    prs.dismiss(msg, 1)


def exec_git(prs):
    """Executes a git command. """
    git_dir = expanduser(prs.cmd_token[1][1:-1])
    acl = git.read_acl(git_dir)
    if isinstance(acl, str):
        msg = "EXEC_GIT-ERROR>> acl error: %s" % acl
        prs.dismiss(msg, 1)
    if prs.guest in acl['user']:  # acl['user'] contains acl['admin']
        prs.exec_cmd(prs.cmd, True)
    else:
        msg = "EXEC_GIT-ERROR>> not in acl for `%s`" % git_dir
        prs.dismiss(msg, 1)


def promus_find(prs):
    """Executes the promus-find command """
    git_dir = prs.cmd_token[1]
    acl = git.read_acl(git_dir)
    if isinstance(acl, str):
        msg = "PROMUS_FIND-ERROR>> acl error: %s" % acl
        prs.dismiss(msg, 1)
    if prs.guest in acl['user']:
        prs.exec_cmd(prs.cmd, True)
    else:
        msg = "PROMUS_FIND-ERROR>> not in acl for `%s`" % git_dir
        prs.dismiss(msg, 1)


def exec_unison(prs):
    """Executes the promus-find command """
    prs.log("Executing exec_unison")
    with open('%s/promus.last' % prs.path, 'r') as tmpf:
        info = tmpf.read()
    guest, _, cmd = info.split('\n')
    if guest != prs.guest:
        prs.dismiss("You are not the previous guest ...", 1)
    cmd_token = cmd.split()
    cmd_name = cmd_token[0]
    if cmd_name != 'promus-find':
        prs.dismiss("previous call was not to promus-find ...", 1)

    git_dir = cmd_token[1]
    sys.stderr.write(repr(git_dir))
    acl = git.read_acl(git_dir)
    if isinstance(acl, str):
        msg = "PROMUS_FIND-ERROR>> acl error: %s" % acl
        prs.dismiss(msg, 1)
    if prs.guest in acl['user']:
        prs.exec_cmd(prs.cmd, True)
    else:
        msg = "EXEC_UNISON-ERROR>> not in acl for `%s`" % git_dir
        prs.dismiss(msg, 1)
