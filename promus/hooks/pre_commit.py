"""pre-commit hook

Check that you have modified files which you are allowed to by
looking at the acl.

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

The pre-commit hook is run first, before you even type in a commit
message. It's used to inspect the snapshot that's about to be
committed, to see if you've forgotten something, to make sure tests
run, or to examine whatever you need to inspect in the code. Exiting
non-zero from this hook aborts the commit, although you can bypass it
with git `commit --no-verify`. You can do things like check for code
style (run lint or something equivalent), check for trailing
whitespace (the default hook does exactly that), or check for
appropriate documentation on new methods.

<https://www.kernel.org/pub/software/scm/git/docs/githooks.html>:

This hook is invoked by git commit, and can be bypassed with
`--no-verify option`. It takes no parameter, and is invoked before
obtaining the proposed commit log message and making a commit.
Exiting with non-zero status from this script causes the git commit
to abort.

The default pre-commit hook, when enabled, catches introduction of
lines with trailing whitespaces and aborts the commit when such a
line is found.

All the git commit hooks are invoked with the environment variable
GIT_EDITOR=: if the command will not bring up an editor to modify the
commit message.

"""
from fnmatch import fnmatch
from promus.command import exec_cmd
from promus.core import git


def run(prs):
    """Function to execute when the pre-commit hook is called. """
    prs.attend_master()
    guest = prs.guest

    authorizer = git.GitAuthorizer()
    authorizer.load_users('~/.promus/users')
    authorizer.read_acl(git.local_path())

    admin_files = ['.acl']
    files, _, _ = exec_cmd("git diff-index --cached --name-only HEAD")

    denied = list()
    exceptions = list()
    for mod_file in files.split('\n'):
        mod_file = mod_file.strip()
        if mod_file == '':
            continue
        access = authorizer.has_access(guest, mod_file, admin_files)
        if access is False:
            denied.append(mod_file)
        if mod_file == '.acl':
            try:
                git.check_acl(mod_file)
            except git.ACLException as exception:
                exceptions.append("ACLException: %r" % exception.message)
        elif fnmatch(mod_file, '.*.profile'):
            try:
                git.check_profile(mod_file)
            except git.ProfileException as exception:
                exceptions.append("ProfileException: %r" % exception.message)
    msg = ''
    if denied:
        msg += 'ACL does not allow you to modify:\n\n    '
        msg += '\n    '.join(denied) + '\n'
    if exceptions:
        msg += 'Exceptions were caught:\n\n    '
        msg += '\n    '.join(exceptions) + '\n'
    if msg != '':
        prs.dismiss('pre_commit', msg, 1)
