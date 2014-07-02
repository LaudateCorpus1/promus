"""Unison utility

This module contains functions to synchronize files specified in
`.gitignore` using `unison`.

"""

import os
import sys
import socket
import promus.util as util
import promus.git as git

def has_unison():
    """Return true if unison is available. """
    out, _, _ = util.exec_cmd('which unison')
    return bool(out)


def host_path():
    """Calls promus.git.remote and parses its contents. It returns
    the host and the path. """
    host, path = git.remote_path().split(':')
    if path[0] == '~':
        path = path[2:]
    return host, path


def read_patterns(prs, path):
    """Read the .gitignore file and detect which files will be synced
    by unison. """
    cmd = 'cd %s ; git show HEAD:.gitignore' % path
    ftmp, err, _ = util.exec_cmd(cmd, False)
    if err:
        msg = "while executing `git show HEAD:.gitignore`: %s" % err[:-1]
        prs.dismiss(msg, 1)
    files = list()
    collect = False
    for line in ftmp.split('\n'):
        tmp = line.split('#')
        if len(tmp) > 1 and 'promus' in tmp[1].lower():
            collect = True
        elif len(tmp) == 1 and tmp[0] == '':
            collect = False
        if collect is True:
            tmpstr = tmp[0].strip()
            if tmpstr:
                files.append(tmpstr)
    return files


def write_unison_output(out, err, local_git):
    """Helper function for unison. """
    if err:
        sys.stderr.write(err)
    out = out.split('\n')
    tmp = '\n'.join([line.split('\r')[-1] for line in out])
    if tmp:
        user = os.environ['USER']
        host = socket.gethostname()
        entry = '[%s %s@%s]$' % (util.date(), user, host)
        cmd = 'find %s -name .bak*' % (local_git)
        backup, _, _ = util.exec_cmd(cmd)
        with open('%s/.unison.out' % local_git, 'a') as tmpf:
            tmpf.write('%s\n' % entry)
            tmpf.write('%s\n' % tmp)
            if backup:
                msg = "WARNING: Local changes have been overwritten. \n" \
                      "Backup files to consider: \n\n"
                tmpf.write(msg)
                tmpf.write('%s\n' % backup)
            tmpf.write('%s\n' % ('-'*95))
        return True
    return False


#pylint: disable=R0914
def unison(prs, verbose=True):
    """Main function to synchronize untracked git files. """
    change = False
    if not has_unison():
        print "ERROR: unison was not found in this system."
        print "  MAC INSTALL: sudo port install unison"
        print "  UBUNTU: apt-get install unison"
        print "  FEDORA: yum install unison"
        return 1, change
    local_git = git.local_path()
    if local_git is None:
        msg = "Working directory is not a git repository. "
        prs.dismiss("ERROR>> %s" % msg, 1)
    rep_name = local_git[local_git.rfind('/')+1:]
    files = read_patterns(prs, local_git)
    if len(files) == 0:
        prs.dismiss("nothing to sync...", 0)
    host, path = host_path()
    qfiles = ["'%s'" % line for line in files]

    prs.log('Retrieving local directories...')
    cmd = 'promus-find %s %s' % (local_git, ' '.join(qfiles))
    local_dirs, _, _ = prs.exec_cmd(cmd)

    prs.log('Retrieving remote directories...')
    cmd = 'ssh %s promus-find %s/unison %s' % (host, path, ' '.join(qfiles))
    remote_dirs, _, _ = prs.exec_cmd(cmd)

    unison_dir = '%s/.unison' % os.environ['HOME']
    util.make_dir(unison_dir)
    unison_file = open('%s/%s.prf' % (unison_dir, rep_name), 'w')
    unison_file.write("# file generated on %s\n" % util.date())
    unison_file.write("root = %s\n" % local_git)
    unison_file.write("root = ssh://%s/%s/unison\n\n" % (host, path))
    unison_file.write("ignore    = Path ./*\n")
    unison_file.write("ignorenot = Path .\n")
    lines = util.merge_lines(local_dirs, remote_dirs)
    lines.remove('')
    for line in lines:
        if line[-1] == '*':
            unison_file.write('ignorenot = Path %s\n' % line)
        else:
            unison_file.write('ignore    = Path %s/*\n' % line)
            unison_file.write('ignorenot = Path %s\n' % line)
    unison_file.write('\nignore    = Name ?*\n')
    unison_file.write('ignore    = Name .*\n')
    for pattern in files:
        unison_file.write('ignorenot = Name %s\n' % pattern)
    unison_file.write('\n')
    content = 'prefer     = ssh://%s/%s/unison\n' \
              'times      = true\n' \
              'logfile    = %s/.git/unison.log\n' \
              'backups    = true\n' \
              'maxbackups = 3\n' % (host, path, local_git)
    unison_file.write(content)
    unison_file.close()

    sys.stdout.write('unison: ')
    sys.stdout.flush()
    cmd = 'unison %s -batch' % rep_name
    unison_out, unison_err, exit_status = util.exec_cmd(cmd, verbose)
    if not verbose:
        change = write_unison_output(unison_out, unison_err, local_git)
    return exit_status, change


def sync(prs):
    """This function gets executed if the --sync options is on. """
    status, _ = unison(prs)
    cmd = 'find %s -name .bak*' % (git.local_path())
    backup, _, _ = util.exec_cmd(cmd)
    if backup:
        msg = '\nWARNING: Local changes have been overwritten.' \
              'Backup files to consider:'
        prs.log(msg)
        prs.log("%s" % backup)
    prs.dismiss("SYNC>> done...", status)

