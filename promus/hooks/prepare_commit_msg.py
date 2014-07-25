"""prepare-commit-msg hook

Prepares the commit message explaining the policy on the commit
messages. It explains that tags can be done during a commit.

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

The `prepare-commit-msg` hook is run before the commit message editor
is fired up but after the default message is created. It lets you
edit the default message before the commit author sees it. This hook
takes a few options: the path to the file that holds the commit
message so far, the type of commit, and the commit SHA-1 if this is
an amended commit. This hook generally isn't useful for normal
commits; rather, it's good for commits where the default message is
auto-generated, such as templated commit messages, merge commits,
squashed commits, and amended commits. You may use it in conjunction
with a commit template to programmatically insert information.

<https://www.kernel.org/pub/software/scm/git/docs/githooks.html>:

This hook is invoked by git commit right after preparing the default
log message, and before the editor is started.

It takes one to three parameters. The first is the name of the file
that contains the commit log message. The second is the source of the
commit message, and can be: message (if a -m or -F option was given);
template (if a -t option was given or the configuration option
commit.template is set); merge (if the commit is a merge or a
.git/MERGE_MSG file exists); squash (if a .git/SQUASH_MSG file
exists); or commit, followed by a commit SHA1 (if a -c, -C or --amend
option was given).

If the exit status is non-zero, git commit will abort.

The purpose of the hook is to edit the message file in place, and it
is not suppressed by the `--no-verify` option. A non-zero exit means
a failure of the hook and aborts the commit. It should not be used as
replacement for pre-commit hook.

The sample prepare-commit-msg hook that comes with git comments out
the Conflicts: part of a merge's commit message.

"""

import sys

MSG = """

"""

def run(_):
    """Function to execute when the prepare-commit-msg hook is called. """
    commit_msg_file = sys.argv[1]
    with open(commit_msg_file, 'r') as msgf:
        default_text = msgf.read()
    msgf = open(commit_msg_file, 'w')
    msgf.write(MSG)
    msgf.write(default_text)
    msgf.close()
