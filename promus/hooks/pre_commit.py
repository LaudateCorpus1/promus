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
import promus.core as prc


ADMIN_FILES = ['.acl', '.description', '.bashrc', '.gitignore']
MSG = 'PRE-COMMIT>> You do not have access to modify "%s"'
MSG_ADMIN = 'PRE-COMMIT>> You must be an admin to modify "%s"'


def zip_list(acl, key):
    "Zip the list to handle two items at a time. "
    return zip(acl[key][0::2], acl[key][1::2])


def check_names(acl, user, mod_file):
    "Checks mod_file against the acl names. "
    has_access = None
    for names, users in zip_list(acl, 'name'):
        if prc.file_match(mod_file, names):
            has_access = prc.has_access(user, users)
            break
    return has_access


def check_paths(acl, user, mod_file):
    "Checks mod_file against the acl paths. "
    has_access = None
    for paths, users in zip_list(acl, 'path'):
        if prc.file_in_path(mod_file, paths):
            has_access = prc.has_access(user, users)
            break
    return has_access


def run(prs):
    """Function to execute when the pre-commit hook is called. """
    acl = prc.read_acl(prc.local_path())
    if isinstance(acl, str):
        prs.dismiss("PRE-COMMIT>> Skipping due to acl error: %s" % acl, 0)
    out, _, _ = exec_cmd("git diff-index --cached --name-only HEAD")
    user = prs.master
    user_files = ['.%s.profile' % usr for usr in acl['user']]
    for mod_file in out.split('\n'):
        if mod_file == '':
            continue
        if mod_file in ADMIN_FILES:
            if user in acl['admin']:
                if mod_file == '.acl':
                    tmp = prc.check_acl("%s/.acl" % prc.local_path())
                    if isinstance(tmp, str):
                        prs.dismiss("PRE-COMMIT>> acl error: %s" % tmp, 1)
                continue
            else:
                prs.dismiss(MSG_ADMIN % mod_file, 1)
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
