"""GIT TEST

To run:

    nosetests -vs test_git

For a single test:

    nosetests -vs test_git:name_of_test

"""
from nose.tools import eq_
from promus.core import util, git


def test_read_acl():
    """git.read_acl: """
    git_autho = git.GitAuthorizer()
    git_autho.load_users('files/users_01.txt')
    git_autho.parse_acl(util.read_file("files/acl_01.txt"))
    list_test = [
        ('daisy', None, True),
        ('daisy', 'docs/other/text.html', False),
        ('daisy', '.acl', True),
        ('daisy', 'dir1/file.html', True),
        ('user5@host', 'dir1/sub/other.tex', False),
        ('jmlopez', 'anyfile', True),
        ('unknown', '.acl', False),
        ('beta', None, False),
        ('user2', 'dir1/some/path/to/file1.html', True),
        ('user3', 'dir1/some/path/to/file1.tex', True),
    ]
    for user, mod_file, val in list_test:
        eq_(
            git_autho.has_access(user, mod_file),
            val,
            '%r access to %r' % (user, mod_file)
        )
