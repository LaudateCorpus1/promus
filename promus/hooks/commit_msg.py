"""commit_msg hook

Format the message so that it wraps at column 70. Check that it has
a title and description and exist with (1) if it does not. Check
the title to see if you wish to create a tag. If you do a commit by
`git commit -m "message"` You may separate the title and description
by '|'. i.e `git commit -m "title|description"

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

The commit-msg hook takes one parameter, which is the path to a
temporary file that contains the current commit message. If this
script exits non-zero, Git aborts the commit process, so you can use
it to validate your project state or commit message before allowing a
commit to go through.

<https://www.kernel.org/pub/software/scm/git/docs/githooks.html>:

This hook is invoked by `git commit`, and can be bypassed with
`--no-verify` option. It takes a single parameter, the name of the
file that holds the proposed commit log message. Exiting with
non-zero status causes the git commit to abort.

The hook is allowed to edit the message file in place, and can be
used to normalize the message into some project standard format (if
the project has one). It can also be used to refuse the commit after
inspecting the message file.

The default `commit-msg` hook, when enabled, detects duplicate
"Signed-off-by" lines, and aborts the commit if one is found.

"""

import sys
from textwrap import TextWrapper


def error(prs, msg):
    "Exit and records an error message. "
    prs.dismiss("COMMIT_MSG-ERROR>> %s" % msg, 1)


def get_msg_info_strict(prs, commit_msg_file):
    """Read the file COMMITMSG provided by git and extract the title
    and description of the commit message. It exists with 1 if it
    does not find one. """
    with open(commit_msg_file, 'r') as msgf:
        msg = msgf.read()
    lines = [line for line in msg.split('\n') if line and line[0] != '#']
    if len(lines) == 1:
        tmp = lines[0].split("|")
        if len(tmp) == 2:
            return tmp[0], tmp[1]
        if len(tmp) == 3:
            return '|'.join(tmp[0:2]), tmp[2]
        msg = 'Commit message one line format is ' \
              '"title|description" or "title|name|extended-description"'
        error(prs, msg)
    if len(lines) < 2:
        error(prs, "No commit msg found.")
    title = lines[0].strip()
    if title == '':
        error(prs, "No title found in commit msg.")
    description = '\n'.join(lines[1:]).strip()
    if description == '':
        error(prs, "No description found in commit msg.")
    return title, description


def get_msg_info(prs, commit_msg_file):
    """Read the file COMMITMSG provided by git and extract the title
    and description of the commit message. It exists with 1 if it
    does not find one. """
    with open(commit_msg_file, 'r') as msgf:
        msg = msgf.read()
    lines = [line for line in msg.split('\n') if line and line[0] != '#']
    if len(lines) == 1:
        tmp = lines[0].split("|")
        if len(tmp) == 2:
            return tmp[0], tmp[1]
        if len(tmp) == 3:
            return '|'.join(tmp[0:2]), tmp[2]
        return tmp[0], ''
    if len(lines) < 2:
        error(prs, "No commit msg found.")
    title = lines[0].strip()
    description = '\n'.join(lines[1:]).strip()
    return title, description


def run(prs):
    """Function to execute when the update hook is called. """
    commit_msg_file = sys.argv[1]
    title, description = get_msg_info(prs, commit_msg_file)
    # You may examine and modify the title and description here.
    # The description will now be modified so that it wraps at
    # line 70.
    wrapper = TextWrapper(width=70, break_long_words=False)
    description = '\n'.join(wrapper.wrap(description))
    # Rewrite the commit_msg_file
    with open(commit_msg_file, 'w') as msgf:
        msgf.write("%s\n\n" % title)
        msgf.write(description)
        msgf.write("\n")
