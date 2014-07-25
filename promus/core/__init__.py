""" Promus core

This package contains the object that executes commands on your
behave as well as other utility functions.

"""

from promus.core.ssh import (
    make_key,
    get_keys,
    get_public_key,
    read_config,
    write_config,
    read_authorized_keys,
    write_authorized_keys,
)
from promus.core.git import (
    config,
    describe,
    repo_name,
    local_path,
    remote_path,
    make_hook,
    init,
    parse_dir,
    parse_acl,
    check_acl,
    read_acl,
    parse_profile,
    check_profile,
    read_profile,
    file_in_path,
    has_access,
    file_match,
    clone,
)
from promus.core.util import (
    is_exe,
    external_executables,
    check_promus_dependencies,
    user_input,
    encrypt_to_file,
    decrypt_from_file,
    wrap_msg,
    make_dir,
    parse_list,
    tokenizer,
    merge_lines,
    strip,
    send_mail,
)

import socket

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


