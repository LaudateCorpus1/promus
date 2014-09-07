"""CORE

This package contains the object that executes commands on your
behalf as well as other utility functions.

"""
import sys
import os.path as pth
from promus.command import warn, error
from . import util, git, user, ssh, cmd


class Promus(object):
    """Handle commands issued over ssh."""

    def __init__(self):
        self.guest = None
        # LOG FILE
        self._path = pth.expanduser('~/.promus')
        util.make_dir(self._path)
        self._log_file = open('{0}/promus.log'.format(self._path), 'a')
        # EXECUTE COMMANDS
        # self.execute

    def log(self, msg):
        """Write a message to the log file. """
        warn("[PROMUS]: {0}\n".format(msg))
        msg = '[{date}:~ {guest}:{key}]$ {msg}\n'.format(
            date=util.date(True),
            guest=self.guest.email,
            msg=msg,
            key=self.guest.key[-10:],
        )
        self._log_file.write(msg)

    def dismiss(self, msg, status):
        """Print msg to the standard error stream as well as to the
        log file and exit with the provided status. """
        self.log(msg)
        self._log_file.close()
        sys.exit(status)

    def greet(self):
        """Handle the guest request. """
        try:
            self.guest = user.get_promus_user()
        except RuntimeError as exception:
            msg = "GREET-ERROR>> unable to greet guest: {0}"
            self.dismiss(msg.format(exception.message), 1)
        self.log("GREET>> connected as {0}".format(self.guest.email))
        if not self.guest.cmd_ok:
            msg = "GREET-ERROR>> more than one command: {0}"
            self.dismiss(msg.format(self.guest.cmd), 1)
        self.log("GREET>> command: %r" % self.guest.cmd)
        token = self.guest.cmd_token
        if self.guest.cmd_name == 'pyfunc':
            if token[1] not in cmd.PY_MAP:
                self.dismiss(
                    "GREET-ERROR: no pyfunc '%s' defined\n" % token[1], 1
                )
            try:
                cmd.PY_MAP[token[1]](self, *(token[2:]))
            except TypeError as exception:
                self.dismiss("GREET-ERROR: %s\n" % exception.message, 1)
        else:
            if token[0] not in cmd.CMD_MAP:
                self.dismiss(
                    "GREET-ERROR: no wrapper for '%s' defined" % token[0], 1
                )
            cmd.CMD_MAP[token[0]](self)
        self.dismiss("GREET>> done", 0)
