"""GIT

In this package we can find functions designed to obtain information
from a git repository.

"""
import six
import json
import os.path as pth
from fnmatch import fnmatch
from promus.command import exec_cmd
from promus.core import util


class ACLException(Exception):
    """Raised when parsing an ACL string. """
    pass


class NoACLException(Exception):
    """Raised solely when the git repository cannot find the acl
    file. """
    pass


class ProfileException(Exception):
    """Raised when parsing a profile string. """
    pass


class NoProfileException(Exception):
    """Raised when the git repository cannot find a guest profile. """
    pass


def config(entry, val=None, global_setting=True):
    """Call `git config --global` when `global_setting` is set to
    True, otherwise call `git config` to set or get an entry. """
    cmd = 'git config '
    if global_setting:
        cmd += '--global '
    if val:
        exec_cmd('{0} {1} "{2}"'.format(cmd, entry, val))
    else:
        val, _, _ = exec_cmd('{0} {1}'.format(cmd, entry))
    return util.strip(val)


def describe():
    "Return last tag, number of commits and sha. "
    out, _, status = exec_cmd('git describe --long')
    if status != 0:
        return None, 0, None
    out = out.split('-')
    return out[0], out[1], out[2][1:]


def repo_name(local=True):
    "Return the name of the repository. "
    if local:
        cmd = 'basename `git rev-parse --show-toplevel`'
    else:
        cmd = 'basename `pwd`'
    out, _, _ = exec_cmd(cmd)
    return util.strip(out)


def local_path():
    "Return the path to directory containing the `.git` directory. "
    out, _, _ = exec_cmd('git rev-parse --show-toplevel')
    return util.strip(out)


def remote_path():
    "Return the path of the remote repository. "
    out, _, _ = exec_cmd('git config --get remote.origin.url')
    return util.strip(out)


HOOK_TEMPLATE = '''#!/usr/bin/env python
"""{hook} hook generated on {date}"""
from promus.core import Promus
import promus.hooks.{hookpy} as hook

if __name__ == "__main__":
    PRS = Promus()
    hook.run(PRS)
    PRS.dismiss("{hook}", "done", 0)
'''


def make_hook(hook, path):
    "Creates the specified hook. "
    hook_file = "%s/%s" % (path, hook)
    if pth.exists(hook_file):
        cmd = "mv %s %s.%s" % (hook_file, hook_file, util.date(True))
        exec_cmd(cmd, True)
    hookpy = hook.replace('-', '_')
    content = HOOK_TEMPLATE.format(hook=hook, hookpy=hookpy,
                                   date=util.date())
    with open(hook_file, 'w') as hookfp:
        hookfp.write(content)
    exec_cmd('chmod +x %s' % hook_file, True)


class GitAuthorizer(object):
    """Create an object to aprove access to a git repository. """

    def __init__(self):
        self.admin = list()
        self.user = dict()
        self.team = dict()
        self.host_users = dict()

    def load_users(self, user_file):
        """Read the specified file and populate the attribute
        `host_users`."""
        try:
            file_obj = open(pth.expanduser(user_file), 'r')
        except IOError:
            return self.host_users
        try:
            self.host_users = json.load(file_obj)
        except ValueError:
            return self.host_users
        file_obj.close()
        return self.host_users

    def get_user_email(self, key):
        """Return a users valid email. If no email is found then
        return None. """
        for email, item in six.iteritems(self.host_users):
            if key == email:
                return email
            for _, prop in six.iteritems(item):
                if key == prop['user'] or key in prop['name'].lower():
                    return email
        return None

    def _update_admin_list(self, val):
        """Helper method for parse_acl. """
        admins = util.split_at(',', val)
        for item in admins:
            admin = self.get_user_email(item.strip())
            if admin and admin not in self.admin:
                self.admin.append(admin)

    def _update_user_list(self, val):
        """Helper method for parse_acl. """
        users = util.split_at(',', val)
        for item in users:
            email = self.get_user_email(item.strip())
            if email and email not in self.user:
                self.user[email] = list()

    def _update_team_list(self, val, line_num):
        """Helper method for parse_acl. """
        try:
            tmp = val.split('|')
            teams = util.split_at(',', tmp[0])
            users = util.split_at(',', tmp[1])
        except IndexError:
            err_msg = "'|' not found in line %d" % line_num
            raise ACLException(err_msg)
        emails = list()
        for item in users:
            email = self.get_user_email(item.strip())
            if email and email not in emails:
                emails.append(email)
        for team_name in teams:
            self.team[team_name.strip()] = emails

    def _update_user_pattern(self, email, action, patterns):
        """Helper method for _update_user_access. """
        for pattern in patterns:
            self.user[email].append((pattern.strip(), action == '!allow'))

    def _update_user_access(self, val, line_num):
        """Helper method for parse_acl. """
        try:
            tmp = val.split('|')
            patterns = util.split_at(',', tmp[0])
            users = util.split_at(',', tmp[1])
        except IndexError:
            err_msg = "'|' not found in line %d" % line_num
            raise ACLException(err_msg)
        action = '!allow'
        for item in users:
            item = item.strip().lower()
            if item in ['!deny', '!allow']:
                action = item
                continue
            if item == '!all':
                for email in self.user:
                    self._update_user_pattern(email, action, patterns)
            elif item.startswith('!team:'):
                team_name = item[6:]
                if team_name not in self.team:
                    err_msg = "%r team has not been declared" % team_name
                    raise ACLException(err_msg)
                for email in self.team[team_name]:
                    self._update_user_pattern(email, action, patterns)
            else:
                email = self.get_user_email(item)
                if email:
                    self._update_user_pattern(email, action, patterns)
                else:
                    err_msg = "%r is not a valid user" % item
                    raise ACLException(err_msg)

    def parse_acl(self, aclstring):
        """The format of the aclstring is as follows:

            admin: user1
            user: user2, user3, user4, user5
            team: red | user2, user3
            team: blue | user4, user5
            name: * | !deny, !all
            name: dir1/*, dir2/* | !allow, user2, user4
            name: dir1/*.html | !allow, user3, user5
            name: *.tex | !allow, !team:red
            name: *.md | !allow, !team:blue

        This allow us to specify the users for a repository and to
        give more control over the files. By default all the users
        are allowed to modify the files. In the example above we
        first deny access to all files to all the users. Then we
        selectively assign access to the files. The opposite can be
        done as well. This function must be called before we can ask
        the GitAuthorizer if a user has access or not. """
        self.admin = list()
        self.user = dict()
        line_num = 0
        for line in aclstring.split('\n'):
            line = line.strip()
            line_num += 1
            if line == '' or line[0] == '#':
                continue
            try:
                key, val = line.split(':', 1)
                key = key.strip().lower()
                val = val.lower()
            except ValueError:
                err_msg = "wrong number of ':' in line %d" % line_num
                raise ACLException(err_msg)
            if key == 'admin':
                self._update_admin_list(val)
            elif key == 'user':
                self._update_user_list(val)
            elif key == 'team':
                self._update_team_list(val, line_num)
            elif key == 'name':
                self._update_user_access(val, line_num)
            else:
                err_msg = "wrong keyword in line %d" % line_num
                raise ACLException(err_msg)

    def has_access(self, user, mod_file=None, sudo=None):
        """Determine if the user can access a repository. When
        specifying the third parameter it checks if the user can
        modify the file. """
        if isinstance(user, six.string_types):
            email = self.get_user_email(user)
        else:
            try:
                email = user.email
            except AttributeError:
                return False
        if email in self.admin:
            return True
        access = False
        if email in self.user:
            access = True
        if access is False or mod_file is None:
            return access
        if sudo is None:
            sudo = ['.acl']
        for fname in sudo:
            if fnmatch(mod_file, fname):
                access = False
        for pattern, value in self.user[email]:
            if fnmatch(mod_file, pattern):
                access = value
        return access

    def read_acl(self, git_dir=None):
        """Read acl from the git repository."""
        if git_dir:
            cmd = 'cd %s; git show HEAD:.acl' % git_dir
        else:
            cmd = 'git show HEAD:.acl'
        aclfile, err, _ = exec_cmd(cmd)
        if err:
            raise NoACLException(err[:-1])
        return self.parse_acl(aclfile)


def check_acl(aclfile):
    """Attempts to read the acl file to see if it contains any
    errors. """
    try:
        aclfile = util.read_file(aclfile)
    except IOError:
        raise NoACLException("acl not found: '%s'" % aclfile)
    git_authorizer = GitAuthorizer()
    git_authorizer.load_users('~/.promus/users')
    git_authorizer.parse_acl(aclfile)


def parse_profile(profilestring):
    """Return profile dictionary. The format of the profilestring is
    as follows:

        email: user@domain.com
        notify: [all/false/track]
        track-files: pattern1, pattern2, ...

    The track-files keyword will only be relevant if notify is set to
    `track`. This tells promus to send a notification to the
    specified email address if one of the modified files matches a
    pattern. Only one keyword and options per line. You may use
    several track-files keywords. """
    profile = dict()
    profile['email'] = ''
    profile['notify'] = 'false'
    profile['track-files'] = list()
    line_num = 0
    for line in profilestring.split('\n'):
        line_num += 1
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        try:
            key, val = line.split(':')
            key = key.strip().lower()
        except ValueError:
            err_msg = "wrong number of ':' in line %d" % line_num
            raise ProfileException(err_msg)
        if key in 'email':
            profile[key] = val.strip()
        elif key in ['notify']:
            val = val.strip().lower()
            if val in ['all', 'false', 'track']:
                profile[key] = val
            else:
                err_msg = "Notify options allowed: all/false/track"
                raise ProfileException(err_msg)
        elif key == 'track-files':
            profile[key].extend(util.split_at(',', val))
        else:
            err_msg = "wrong keyword in line %d" % line_num
            raise ProfileException(err_msg)
    return profile


def check_profile(profile_file):
    "Attempts to read the acl file to see if it contains any errors. "
    try:
        profile = util.read_file(profile_file)
    except IOError:
        raise NoProfileException("profile not found: %r" % profile_file)
    return parse_profile(profile)


def read_profile(user, git_dir=None):
    "Read profile from the git repository."
    if git_dir:
        cmd = 'cd %s; git show HEAD:.%s.profile' % (git_dir, user)
    else:
        cmd = 'git show HEAD:.%s.profile' % user
    profile, err, _ = exec_cmd(cmd, False)
    if err:
        raise NoProfileException("profile not found: .%r.profile" % user)
    return parse_profile(profile)


def load_repos():
    """Obtain the cloned git repositories. """
    try:
        file_obj = open(pth.expanduser('~/.promus/repos'), 'r')
    except IOError:
        return dict()
    try:
        repos = json.load(file_obj)
    except ValueError:
        return dict()
    file_obj.close()
    return repos


def dump_repos(repos):
    """Store the git repositories. """
    with open(pth.expanduser('~/.promus/repos'), 'w') as fp_:
        json.dump(
            repos,
            fp_,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
