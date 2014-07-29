"""post-merge hook

It currently does nothing.

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

The `post-merge` hook runs after a successful merge command. You can use
it to restore data in the working tree that Git can't track, such as
permissions data. This hook can likewise validate the presence of
files external to Git control that you may want copied in when the
working tree changes.

<https://www.kernel.org/pub/software/scm/git/docs/githooks.html>:

This hook is invoked by git merge, which happens when a git pull is
done on a local repository. The hook takes a single parameter, a
status flag specifying whether or not the merge being done was a
squash merge. This hook cannot affect the outcome of git merge and is
not executed, if the merge failed due to conflicts.

This hook can be used in conjunction with a corresponding pre-commit
hook to save and restore any form of metadata associated with the
working tree (eg: permissions/ownership, ACLS, etc). See
contrib/hooks/setgitperms.perl for an example of how to do this.

"""


def run(_):
    """Function to execute when the post-merge hook is called. """
    pass
