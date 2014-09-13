"""Sync Utilities"""

import os
import socket
import os.path as pth
from datetime import datetime
from six.moves import cPickle as pickle
from promus.command import (
    exec_cmd,
    disp,
    c_msg,
    c_error,
    c_disp,
    c_warn
)


def dump_config(config):
    """Store a sync configuration. """
    with open(pth.expanduser('~/.promus/promus-sync'), 'w') as tmp:
        pickle.dump(config, tmp)


def load_config():
    """Load a sync configuration. """
    try:
        with open(pth.expanduser('~/.promus/promus-sync'), 'r') as tmp:
            config = pickle.load(tmp)
    except IOError:
        config = list()
    return config


def print_entry(config, index):
    """Display an entry of the configuration. """
    entry = config[index]
    if entry[3] == datetime(1, 1, 1):
        sync_date = '     Never Synced     '
    else:
        sync_date = entry[3].strftime("%b/%d/%Y - %H:%M:%S")
    msg = '{lb} {index} {rb}{lb} {sync_date} {rb}'
    if entry[0] != '':
        msg += '{lb} {alias} {rb}{colon} '
    else:
        msg += '{colon} '
    msg += '{local} <==> {remote}\n'
    msg = msg.format(
        lb=c_msg('BD', '['),
        rb=c_msg('BD', ']'),
        colon=c_msg('BD', ':'),
        index=c_msg('G', index),
        sync_date=c_msg('R', sync_date),
        alias=c_msg('G', entry[0]),
        local=c_msg('C', entry[1]),
        remote=c_msg('C', entry[2]),
    )
    disp(msg)


def register(local, remote, alias):
    """Register a pair of directories to sync. """
    config = load_config()
    local = pth.abspath(local)
    if not pth.isdir(local):
        c_error('"%s" does not exist in this machine.' % local)
    if local[-1] != '/':
        local += '/'
    if not pth.isdir(remote):
        tmp = remote.split(':')
        if len(tmp) == 1:
            c_error('The remote path does not exist')
        cmd = "ssh %s 'cd %s'" % (tmp[0], tmp[1])
        _, _, exit_code = exec_cmd(cmd)
        if exit_code != 0:
            c_error('Verify hostname and remote directory.')
    if remote[-1] != '/':
        remote += '/'
    config.append([alias, local, remote, datetime(1, 1, 1)])
    dump_config(config)
    entry_file = pth.expanduser('~/.promus/sync-%d.txt' % (len(config)-1))
    open(entry_file, 'w').close()
    c_disp('B', 'Registration successful. \n')


def unregister(index):
    """Remove an entry. """
    try:
        index = int(index)
    except (ValueError, TypeError):
        c_error("provide a valid index")
    config = load_config()
    if index < 0 or index >= len(config):
        c_error("invalid entry index")
    c_warn('Are you sure you want to delete this entry:')
    print_entry(config, index)
    choice = raw_input(c_msg('BD', "[yes/no] => ")).lower()
    if choice in ['yes', 'y']:
        del config[index]
        dump_config(config)
        home = os.environ['HOME']
        try:
            os.remove('%s/.promus/sync-%d.txt' % (home, index))
        except OSError:
            pass
        while index < len(config):
            old = '%s/.promus/sync-%d.txt' % (home, index+1)
            new = '%s/.promus/sync-%d.txt' % (home, index)
            os.rename(old, new)
            index += 1
    elif choice in ['no', 'n']:
        pass
    else:
        c_error("respond with 'yes' or 'no'")


def set_alias(index, alias):
    """Modify the alias of an entry. """
    if index is None:
        c_error("Need an alias or entry number as argument.")
    config = load_config()
    if index.isdigit():
        index = [int(index)]
    else:
        index = [i for i, v in enumerate(config) if v[0] == index]
    if not index:
        c_warn("There is no entry to modify.")
        return
    for num in index:
        try:
            config[num]
        except IndexError:
            c_error("Invalid entry number. ")
        config[num][0] = alias
        c_disp('B', '%d <==> %s\n' % (num, alias))
    dump_config(config)


def reset_date(index):
    """Reset the last sync date. """
    try:
        index = int(index)
    except (ValueError, TypeError):
        c_error("provide a valid index")
    config = load_config()
    if index < 0 or index >= len(config):
        c_error("invalid entry index")
    c_warn('Are you sure you want to reset the last sync date on:')
    print_entry(config, index)
    choice = raw_input(c_msg('BD', "[yes/no] => ")).lower()
    if choice in ['yes', 'y']:
        config[index][3] = datetime(1, 1, 1)
        dump_config(config)
        home = os.environ['HOME']
        open('%s/.promus/sync-%d.txt' % (home, index), 'w').close()
    elif choice in ['no', 'n']:
        pass
    else:
        c_error("respond with 'yes' or 'no'")


def _explore_remote(local, remote):
    """Call rsync remote to local to see which files will be
    transfering to local and which files are missing in the remote.
    Returns the list of incoming files and the list of files missing
    in the remote. """
    disp('* receiving list of incoming files ... ')
    cmd = 'rsync -nravz --delete --exclude .DS_Store ' \
          '--out-format="%n<>%M" {0} {1}'.format(remote, local)
    out, _, _ = exec_cmd(cmd)
    tmp_files = out.split('\n')[1:-4]
    incoming = list()
    remote_missing = list()
    for file_ in tmp_files:
        entry = file_.split('<>')
        if len(entry) > 1:
            incoming.append(
                (entry[0], datetime.strptime(entry[1], '%Y/%m/%d-%H:%M:%S'))
            )
        else:
            remote_missing.append(file_.split(' ', 1)[1])
    disp('done\n')
    return incoming, remote_missing


def _analyze_incoming(num, incoming, local, sync_date):
    """Study the incoming files to avoid overwriting of files. """
    if incoming:
        disp('  - analysing %d incoming files\n' % len(incoming))
    exclude = open('%s/.promus/tmp.txt' % os.environ['HOME'], 'w')
    for in_index, in_file in enumerate(incoming):
        disp('    [{0}/{1}]: '.format(in_index+1, len(incoming)))
        if pth.isfile(local+in_file[0]):
            local_time = datetime.fromtimestamp(pth.getmtime(local+in_file[0]))
            if local_time > sync_date:
                if in_file[1] > sync_date:
                    (dir_name, file_name) = pth.split(in_file[0])
                    new_name = '{dir}/({host})({date})_{name}'.format(
                        dir=dir_name,
                        host=socket.gethostname(),
                        date=local_time.strftime("%Y_%m_%d-%H_%M_%S"),
                        name=file_name
                    )
                    c_disp('C', in_file[0])
                    c_disp('Y', ' will be renamed to "')
                    c_disp('C', new_name)
                    disp('".\n')
                    os.rename(local+in_file[0], local+new_name)
                else:
                    disp(c_msg('C', in_file[0]))
                    disp(c_msg('R', ' has been modified locally.\n'))
            else:
                disp(c_msg('C', in_file[0]))
                disp(' has not been modified.\n')
        elif pth.isdir(local+in_file[0]):
            disp(c_msg('C', in_file[0]))
            disp(' is an existing directory.\n')
        else:
            disp(c_msg('C', in_file[0]))
            disp(c_msg('Y', ' may be excluded.\n'))
            exclude.write(in_file[0]+'\n')
    exclude.close()
    # To find lines common to two files
    # http://www.unix.com/shell-programming-scripting/144741-simple-script-find-common-strings-two-files.html
    cmd = 'grep -Fxf {home}/.promus/tmp.txt {home}/.promus/sync-{num}.txt ' \
          '> {home}/.promus/exclude.txt'
    exec_cmd(cmd.format(home=os.environ['HOME'], num=num), True)


def _analyse_remote_missing(num, remote_missing, local, sync_date):
    """Analyze the list of missing files in the remote to avoid local
    deletion of files. """
    if remote_missing:
        disp('  - analysing %d missing files in remote\n' % len(remote_missing))
    remove = open('%s/.promus/tmp.txt' % os.environ['HOME'], 'w')
    for index, file_ in enumerate(remote_missing):
        disp('    [{0}/{1}]: '.format(index+1, len(remote_missing)))
        if os.path.isfile(local+file_):
            if datetime.fromtimestamp(pth.getmtime(local+file_)) > sync_date:
                disp(c_msg('C', file_))
                disp(' has been modified - will not be deleted.\n')
            else:
                disp(c_msg('C', file_))
                disp(c_msg('Y', ' may require deletion.\n'))
                remove.write(file_+'\n')
        else:
            disp('Directory ')
            disp(c_msg('C', file_))
            disp(c_msg('Y', ' may require deletion.\n'))
            remove.write(file_+'\n')
    remove.close()
    cmd = 'grep -Fxf {home}/.promus/tmp.txt {home}/.promus/sync-{num}.txt ' \
          '> {home}/.promus/remove.txt'
    exec_cmd(cmd.format(home=os.environ['HOME'], num=num), True)


def _remote_to_local(remote, local):
    """Call rsync. """
    disp('* remote --> local (update: no deletion) ... ')
    cmd = "rsync -razuv --exclude-from '%s/.promus/exclude.txt' %s %s"
    cmd = cmd % (os.environ['HOME'], remote, local)
    _, _, code = exec_cmd(cmd)
    if code != 0:
        c_error('rsync returned error code: %d' % code)
        exit(code)
    disp('done\n')


def _local_to_remote(local, remote):
    """Call rsync. """
    disp('* local --> remote (delete) ... ')
    cmd = "rsync -razuv --delete %s %s" % (local, remote)
    _, _, code = exec_cmd(cmd)
    if code != 0:
        c_error('rsync returned error code: %d' % code)
        exit(code)
    disp('done\n')


def _clean_local(local):
    """Delete local files. """
    with open('%s/.promus/remove.txt' % os.environ['HOME'], 'r') as tmp:
        lines = tmp.readlines()
    if lines:
        disp("* deleting %d files/directories ...\n" % len(lines))
    index = 0
    for file_ in reversed(lines):
        disp('  [{0}/{1}]: '.format(index+1, len(lines)))
        fname = local + file_[0:-1]
        if fname[-1] == '/':
            try:
                os.rmdir(fname)
                c_disp('C', fname)
                c_disp('R', ' has been deleted\n')
            except OSError:
                c_disp('R', 'ERROR: Unable to delete ')
                c_disp('C', fname+'\n')
        else:
            try:
                os.remove(fname)
                c_disp('C', fname)
                c_disp('R', ' has been deleted\n')
            except OSError:
                c_disp('R', 'ERROR: Unable to delete ')
                c_disp('C', fname+'\n')
        index += 1


def _record_sync(config, num, local):
    """Save sync date. """
    config[num][3] = datetime.now()
    msg = "* saving sync date: %s ... "
    msg = msg % config[num][3].strftime("%b/%d/%Y - %H:%M:%S")
    disp(msg)
    dump_config(config)
    cmd = 'cd %s;'
    # Make find show slash after directories
    #  http://unix.stackexchange.com/a/4857
    cmd += 'find . -type d -exec sh -c \'printf '
    cmd += r'"%%s/\n" "$0"\' {} \; -or -print'
    # Need to delete ./ from the path:
    #  http://stackoverflow.com/a/1571652/788553
    cmd += ' | sed s:"./":: > %s/.promus/sync-%d.txt'
    cmd = cmd % (local, os.environ["HOME"], num)
    exec_cmd(cmd, True)
    # os.remove('%s/.promus/tmp.txt' % HOME)
    # os.remove('%s/.promus/exclude.txt' % HOME)
    # os.remove('%s/.promus/remove.txt' % HOME)
    disp('done\n')


def _sync(config, num):
    """Sync an entry in the configuration. """
    print_entry(config, num)
    local = config[num][1]
    remote = config[num][2]
    sync_date = config[num][3]
    # RECEVING INCOMING
    incoming, remote_missing = _explore_remote(local, remote)
    # ANALYSE INCOMING
    _analyze_incoming(num, incoming, local, sync_date)
    # ANALYSE REMOTE
    _analyse_remote_missing(num, remote_missing, local, sync_date)
    # REMOTE TO LOCAL
    _remote_to_local(remote, local)
    # CLEAN LOCAL
    _clean_local(local)
    # LOCAL TO REMOTE
    _local_to_remote(local, remote)
    # RECORD SYNC
    _record_sync(config, num, local)


def sync_entry(index):
    """Synchronize an entry. """
    config = load_config()
    if index.isdigit():
        index = [int(index)]
    else:
        index = [i for i, v in enumerate(config) if v[0] == index]
    if not index:
        c_warn("Nothing to sync.")
        return
    for num in index:
        try:
            config[num]
        except IndexError:
            c_error("Invalid entry number/alias. ")
        _sync(config, num)
