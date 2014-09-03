"""CORE

This package contains the object that executes commands on your
behalf as well as other utility functions.

"""
import sys
import os.path as pth
from promus.command import warn
from . import util, git, user, ssh


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
        msg = '[{date}:~ {guest}]$ {msg}\n'.format(
            date=util.date(True),
            guest=self.guest.email,
            msg=msg,
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
        # NEEDS TO WRITE COMMAND CODE
        self.dismiss("GREET>> done", 0)
