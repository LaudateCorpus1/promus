"""post-commit hook

It currently does nothing.

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

After the entire commit process is completed, the `post-commit` hook
runs. It doesn't take any parameters, but you can easily get the last
commit by running `git log -1 HEAD`. Generally, this script is used for
notification or something similar.

<https://www.kernel.org/pub/software/scm/git/docs/githooks.html>:

This hook is invoked by `git commit`. It takes no parameter, and is
invoked after a commit is made.

This hook is meant primarily for notification, and cannot affect the
outcome of git commit.

"""

# A few git commands:
#
#   git push origin master:master && git push
#   git push origin --tags


def run(_):
    """Function to execute when the post-commit hook is called. """
    pass
