"""post-receive hook

Email the users of this repository

<http://git-scm.com/book/en/Customizing-Git-Git-Hooks>:

The post-receive hook runs after the entire process is completed and
can be used to update other services or notify users. It takes the
same stdin data as the pre-receive hook. Examples include e-mailing a
list, notifying a continuous integration server, or updating a
ticket-tracking system - you can even parse the commit messages to
see if any tickets need to be opened, modified, or closed. This
script can't stop the push process, but the client doesn't disconnect
until it has completed; so, be careful when you try to do anything
that may take a long time.

"""

from promus.command import exec_cmd
import promus.core as prc
try:
    import cPickle as pickle
except ImportError:
    import pickle
import os


TEXT = """%%s: %B

Changes pushed by %aN on %cD:

%%s

Note: To stop recieving emails from this repository modify
your profile located in the git root: `.user.profile`.

Set the keyword `notify` to false to stop reciving emails or
set to `track` to recieve emails only when files matching
patterns in `tracked-files` have been modified."""

HTML = """<!doctype html>
<html>
<style>
body {
    font-family: "Myriad Pro", Calibri, Helvetica, Arial, sans-serif;
    width: 500px;
    font-size: 16px;
}
h3.title {
    margin-top: 0;
    font-variant: small-caps;
}
code {
    font-size: 80%%%%;
    box-sizing: border-box;
    padding: 0px 2px;
    margin: 0 3px;
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.1);
    font-family: "Lucida Console", Terminal, monospace;
}
ul {
    list-style-type: square;
}
p.footer {
    font-size: 12px;
}
</style>
<body>
<h3 class="title">[%%s]: %s</h3>
<p>%b</p><hr>
<p>Changes pushed by <strong>%aN</strong> on <em>%%s</em>:</p>
<ul>
%%s
</ul>
<p class="footer"><strong>Note:</strong> To stop recieving emails from
this repository modify your profile located in the git root:
<code>.user.profile</code>.</p>
<p class="footer">Set the keyword <code>notify</code> to <code>false</code> to
stop reciving emails or set to <code>track</code> to recieve emails
only when files matching patterns in <code>tracked-files</code> have
been modified.
</p>
</body>
</html>"""


def run(prs):
    """Function to execute when the post-receive hook is called. """
    try:
        with open('TMP_NOTIFY.p', 'rb') as tmpf:
            files = pickle.load(tmpf)
            acl = pickle.load(tmpf)
    except IOError as exc:
        prs.dismiss("POST_RECEIVE>> First time commiting?", 0)
    destination = list()
    for user in acl['user']:
        profile = prc.read_profile(user)
        if isinstance(profile, str):
            continue
        if profile['notify'] == 'all':
            destination.append(profile['email'])
        elif profile['notify'] == 'track':
            for fname in files:
                if prc.file_match(fname, profile['track-files']):
                    destination.append(profile['email'])
                    break
                if prc.file_in_path(fname, profile['track-files']):
                    destination.append(profile['email'])
                    break
    prs.log("POST_RECEIVE>> Creating email")
    try:
        cmd = "git log -1 --pretty=format:'[%%s]: %aN - %s'"
        subject, _, _ = exec_cmd(cmd)
        subject = subject.strip() % prc.repo_name(False)
    except Exception as exc:
        prs.dismiss("POST_RECEIVE-ERROR>> %s" % str(exc), 1)
    text, _, _ = exec_cmd("git log -1 --pretty=format:'%s'" % TEXT)
    html, _, _ = exec_cmd("git log -1 --pretty=format:'%s'" % HTML)
    date, _, _ = exec_cmd("git log -1 --pretty=format:'%cD'")
    text_file = ''
    for fname in sorted(files):
        commit = ', '.join([tmp[:7] for tmp in files[fname]])
        text_file += '   - %s: %s\n' % (fname, commit)
    html_file = ''
    for fname in sorted(files):
        commit = ', '.join(["<code>%s</code>" % tmp[:7] for tmp in files[fname]])
        html_file += '<li><strong>%s</strong>: %s</li>\n' % (fname, commit)
    text = text % (prc.repo_name(False), text_file)
    html = html % (prc.repo_name(False), prc.date(date), html_file)
    prc.send_mail(destination, subject, text, html)
    os.remove("TMP_NOTIFY.p")
