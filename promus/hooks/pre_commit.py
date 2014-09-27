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

from promus.command import exec_cmd
from promus.core import git, user

HOOK = 'pre_commit'
MSG = 'PRE-COMMIT>> You do not have access to modify "%s"'
MSG_ADMIN = 'PRE-COMMIT>> You must be an admin to modify "%s"'


def run(prs):
    """Function to execute when the pre-commit hook is called. """
    prs.attend_master()
    guest = prs.guest
    access = guest.has_git_access(git.local_path())
    user_files = ['.%s.profile' % x for x in guest.acl['user']]
    admin_files = ['.acl']
    files, _, _ = exec_cmd("git diff-index --cached --name-only HEAD")
    for mod_file in files.split('\n'):
        mod_file = mod_file.strip()
        if mod_file == '':
            continue
        if mod_file in user_files:
            if mod_file == '.%s.profile' % user or user in acl['admin']:
                tmp = prc.check_profile("%s/.%s.profile" % (prc.local_path(),
                                                            user))
                if isinstance(tmp, str):
                    prs.dismiss("PRE-COMMIT>> profile error: %s" % tmp, 1)
                continue
            else:
                prs.dismiss(MSG % mod_file, 1)
        
        access = guest.has_git_access(None, mod_file, admin_files)

        if mod_file in user_files:
            if mod_file == '.%s.profile' % user or user in acl['admin']:
                tmp = prc.check_profile("%s/.%s.profile" % (prc.local_path(),
                                                            user))
                if isinstance(tmp, str):
                    prs.dismiss("PRE-COMMIT>> profile error: %s" % tmp, 1)
                continue
            else:
                prs.dismiss(MSG % mod_file, 1)
        has_access = check_names(acl, user, mod_file)
        if has_access is True:
            continue
        if has_access is False:
            prs.dismiss(MSG % mod_file, 1)
        has_access = check_paths(acl, user, mod_file)
        if has_access in [True, None]:
            continue
        prs.dismiss(MSG % mod_file, 1)
