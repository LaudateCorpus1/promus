"""tests

Provides functions for unit testing.

"""
from nose.tools import eq_
from promus.command import exec_cmd


def run_cmd(cmd, exp_err, exp_out):
    """Run a command and compare the expected output and error."""
    out, err, _ = exec_cmd(cmd)
    hline = '_'*60
    msg = "%s stderr -->\n%s\n%s\n%s\n\
%s expected stderr -->\n%s\n%s\n%s\n" % (cmd, hline, err, hline,
                                         cmd, hline, exp_err, hline)
    eq_(err, exp_err, msg)
    msg = "%s stdout -->\n%s\n%s\n%s\n\
%s expected stdout -->\n%s\n%s\n%s\n" % (cmd, hline, out, hline,
                                         cmd, hline, exp_out, hline)
    eq_(out, exp_out, msg)


def str_eq(str1, str2):
    """Compare two strings. """
    hline = '_'*60
    msg = "str1 -->\n%s\n%s\n%s\n\
str2 -->\n%s\n%s\n%s\n" % (hline, str1, hline,
                           hline, str2, hline)
    eq_(str1, str2, msg)
