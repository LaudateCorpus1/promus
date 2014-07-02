"""update hook

Check the acl and deny the push if necessary.

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

The update script is very similar to the pre-receive script, except
that it's run once for each branch the pusher is trying to update. If
the pusher is trying to push to multiple branches, pre-receive runs
only once, whereas update runs once per branch they're pushing to.
Instead of reading from stdin, this script takes three arguments: the
name of the reference (branch), the SHA-1 that reference pointed to
before the push, and the SHA-1 the user is trying to push. If the
update script exits non-zero, only that reference is rejected; other
references can still be updated.

<https://www.kernel.org/pub/software/scm/git/docs/githooks.html>:

This hook is invoked by git-receive-pack on the remote repository,
which happens when a git push is done on a local repository. Just
before updating the ref on the remote repository, the update hook is
invoked. Its exit status determines the success or failure of the ref
update.

The hook executes once for each ref to be updated, and takes three
parameters:

 the name of the ref being updated,

 the old object name stored in the ref,

 and the new objectname to be stored in the ref.

A zero exit from the update hook allows the ref to be updated.
Exiting with a non-zero status prevents git-receive-pack from
updating that ref.

This hook can be used to prevent forced update on certain refs by
making sure that the object name is a commit object that is a
descendant of the commit object named by the old object name. That
is, to enforce a "fast-forward only" policy.

It could also be used to log the old..new status. However, it does
not know the entire set of branches, so it would end up firing one
e-mail per ref when used naively, though. The post-receive hook is
more suited to that.

Another use suggested on the mailing list is to use this hook to
implement access control which is finer grained than the one based on
filesystem group.

Both standard output and standard error output are forwarded to git
send-pack on the other end, so you can simply echo messages for the
user.

The default update hook, when enabled and with hooks.allowunannotated
config option unset or set to false prevents unannotated tags to be
pushed.

"""

import sys
import promus.util as util
import promus.git as git
try:
    import cPickle as pickle
except ImportError:
    import pickle

ADMIN_FILES = ['.acl', '.description', '.bashrc', '.gitignore']
MSG = 'UPDATE>> You do not have access to push to "%s"'
MSG_ADMIN = 'UPDATE>> You must be an admin to push to "%s"'
MSG = "UPDATE>> You do not have access to push to another user's profile: %s"

def zip_list(acl, key):
    "Zip the list to handle two items at a time. "
    return zip(acl[key][0::2], acl[key][1::2])


def check_names(acl, user, mod_file):
    "Checks mod_file against the acl names. "
    has_access = None
    for names, users in zip_list(acl, 'name'):
        if git.file_match(mod_file, names):
            has_access = git.has_access(user, users)
            break
    return has_access


def check_paths(acl, user, mod_file):
    "Checks mod_file against the acl paths. "
    has_access = None
    for paths, users in zip_list(acl, 'path'):
        if git.file_in_path(mod_file, paths):
            has_access = git.has_access(user, users)
            break
    return has_access


def add_file(mod_file, rev, files):
    """Add the modified file to the list"""
    if mod_file in files:
        files[mod_file].append(rev)
    else:
        files[mod_file] = [rev]


def run(prs):
    """Function to execute when the update hook is called. """
    prs.attend_last()
    acl = git.read_acl()
    if isinstance(acl, str) and prs.guest == prs.master:
        prs.dismiss("UPDATE>> Skipping due to acl error: %s" % acl, 0)
    if isinstance(acl, str):
        prs.dismiss("UPDATE-ERROR>> acl error: %s" % acl, 1)
    refname = sys.argv[1]
    prs.log("UPDATE>> checking %s" % refname)
    oldrev = sys.argv[2]
    newrev = sys.argv[3]
    user = prs.guest
    user_files = ['.%s.profile' % usr for usr in acl['user']]
    files = dict()
    cmd = "git log -1 --name-only --pretty=format:'' %s"
    commits, _, _ = util.exec_cmd('git rev-list %s..%s' % (oldrev, newrev))
    for rev in commits.split('\n')[:-1]:
        prs.log("UPDATE>> checking revision %s" % rev)
        files_modified, _, _ = util.exec_cmd(cmd % rev)
        for mod_file in files_modified.split('\n'):
            if mod_file == '':
                continue
            add_file(mod_file, rev, files)
            if mod_file in ADMIN_FILES:
                if user in acl['admin']:
                    continue
                else:
                    prs.dismiss(MSG_ADMIN % mod_file, 1)
            if mod_file in user_files:
                if mod_file == ('.%s.profile' % user) or user in acl['admin']:
                    continue
                else:
                    prs.dismiss(MSG_USER % mod_file, 1)
            has_access = check_names(acl, user, mod_file)
            if has_access is True:
                continue
            if has_access is False:
                prs.dismiss(MSG % mod_file, 1)
            has_access = check_paths(acl, user, mod_file)
            if has_access in [True, None]:
                continue
            prs.dismiss(MSG % mod_file, 1)
    with open('TMP_NOTIFY.p', 'wb') as tmpf:
        pickle.dump(files, tmpf)
        pickle.dump(acl, tmpf)
