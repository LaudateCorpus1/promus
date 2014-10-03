<!doctype html>
%%{html}
%%{head}
%%{link rel="stylesheet" type="text/css" href="/static/css/promus-gui.min.css"}
%%{script type="text/javascript" src="/static/js/promus-gui.min.js"}%%
%%%%{body}
Showing keys
============

%%{p #p1}

%%

<?python
import os
import socket
from promus.core import git, ssh

host = socket.gethostname()
master = os.environ['USER']
alias = git.config('host.alias')
id_key, git_key = ssh.get_keys()
id_key = ssh.get_public_key(id_key)
node = __NODE__
p1 = node.owner('#p1')[0]
p1.children(
    "**new stuff**",
    parser_lang="lex",
    convert_from="lex",
    convert_to="html",
    parser_defaults={'inline': 'on'}
)
print '**key**'
print '%s %s@%s - %s\n' % (id_key, master, host, alias)
git_key = ssh.get_public_key(git_key)
print '# GIT_KEY:\n'
print '%s %s@%s - %s - git\n' % (git_key, master, host, alias)
node.owner('#p1').after("**blah**", lang='lex', defaults={'inline':'on'})
?>

%%%%
