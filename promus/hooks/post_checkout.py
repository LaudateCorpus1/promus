"""post-checkout hook

It currently does nothing.

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

After you run a successful git checkout, the post-checkout hook runs;
you can use it to set up your working directory properly for your
project environment. This may mean moving in large binary files that
you don't want source controlled, auto-generating documentation, or
something along those lines.

<https://www.kernel.org/pub/software/scm/git/docs/githooks.html>:

This hook is invoked when a git checkout is run after having updated
the worktree. The hook is given three parameters: the ref of the
previous HEAD, the ref of the new HEAD (which may or may not have
changed), and a flag indicating whether the checkout was a branch
checkout (changing branches, flag=1) or a file checkout (retrieving a
file from the index, flag=0). This hook cannot affect the outcome of
git checkout.

It is also run after git clone, unless the --no-checkout (-n) option
is used. The first parameter given to the hook is the null-ref, the
second the ref of the new HEAD and the flag is always 1.

This hook can be used to perform repository validity checks,
auto-display differences from the previous HEAD if different, or set
working dir metadata properties.

"""


def run(_):
    """Function to execute when the post-checkout hook is called. """
    pass
