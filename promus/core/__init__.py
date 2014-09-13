"""CORE

This package contains the object that executes commands on your
behalf as well as other utility functions.

"""
import sys
import inspect
import os.path as pth
from textwrap import TextWrapper
from promus.command import warn, error, c_msg
from . import util, git, user, ssh, cmd


class Promus(object):
    """Handle commands issued over ssh."""

    def __init__(self):
        self.guest = None
        self._path = pth.expanduser('~/.promus')
        util.make_dir(self._path)
        self._log_file = open('{0}/promus.log'.format(self._path), 'a')

    def log(self, sender, msg, color=None):
        """Write a message to the log file. """
        fmt = "{0}{1} {2}\n"
        if color:
            fmt = fmt.format(
                c_msg('BD', '[PROMUS]: '),
                c_msg('B'+color, sender.upper()+">>"),
                c_msg(color, msg)
            )
            warn(fmt)
        else:
            fmt = fmt.format(
                c_msg('BD', '[PROMUS]: '),
                sender.upper()+">>",
                msg
            )
            warn(fmt)
        msg = '[{date}:~ {guest}:{key}]$ {sender}>> {msg}\n'.format(
            date=util.date(True),
            guest=self.guest.email,
            sender=sender.upper(),
            msg=msg,
            key=self.guest.key[-10:],
        )
        self._log_file.write(msg)

    def dismiss(self, sender, msg, status=0):
        """Print msg to the standard error stream as well as to the
        log file and exit with the provided status. """
        if status != 0:
            self.log(sender+"-ERROR", msg, 'R')
        else:
            self.log(sender, msg)
        self._log_file.close()
        sys.exit(status)

    def greet(self):
        """Handle the guest request. """
        try:
            self.guest = user.get_promus_user()
        except RuntimeError as exception:
            msg = "unable to greet guest: {0}"
            self.dismiss('greet', msg.format(exception.message), 1)
        self.log('greet', "connected as {0}".format(self.guest.email))
        if not self.guest.cmd_ok:
            msg = "more than one command: {0}"
            self.dismiss('greet', msg.format(self.guest.cmd), 1)
        self.log('greet', "command: %r" % self.guest.cmd)
        token = self.guest.cmd_token
        if self.guest.cmd_name == '__DOC__':
            _show_doc(self, token[1])
        elif self.guest.cmd_name == '__PYFUNC__':
            _exec_pyfunc(self, token[1], token[2:])
        else:
            _exec_wrapper(self, token[0])
        self.dismiss('greet', "done", 0)


def _show_doc(prs, func):
    """Display the documentation for the function."""
    if func in cmd.PY_MAP:
        info = cmd.PY_MAP[func]
    elif func in cmd.CMD_MAP:
        info = cmd.CMD_MAP[func]
    else:
        prs.dismiss('show_doc', "'%s' is not defined" % func, 1)
    if not prs.guest.has_access(info[1]):
        prs.dismiss('show_doc', "access denied to '%s'" % func, 1)
    pyfunc = info[0]
    argspec = inspect.getargspec(pyfunc)
    func_doc = "\n{func}{space}{args}:\n    {doc}\n\n".format(
        func=c_msg("BD", func),
        space=' ' if len(argspec[0][1:]) > 0 else '',
        args=', '.join(argspec[0][1:]),
        doc=pyfunc.__doc__
    )
    warn(func_doc)


# pylint: disable=star-args
def _exec_pyfunc(prs, func, args):
    """Execute the python function."""
    if func not in cmd.PY_MAP:
        prs.dismiss('exec_pyfunc', "'%s' is not defined" % func, 1)
    if not prs.guest.has_access(cmd.PY_MAP[func][1]):
        prs.dismiss('exec_pyfunc', "access denied to '%s'" % func, 1)
    try:
        cmd.PY_MAP[func][0](prs, *args)
    except TypeError as exception:
        prs.dismiss('exec_pyfunc', "%s" % exception.message, 1)


def _exec_wrapper(prs, prog):
    """Execute the wrapper for the executable."""
    if prog not in cmd.CMD_MAP:
        prs.dismiss('exec_wrapper', "'%s' is not defined" % prog, 1)
    if not prs.guest.has_access(cmd.CMD_MAP[prog][1]):
        prs.dismiss('exec_wrapper', "access denied to '%s'" % prog, 1)
    cmd.CMD_MAP[prog][0](prs)
