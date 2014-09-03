"""Promus

Here we can find several functions which can be useful outside the
use of the command line use of promus.

"""
import rsa
import socket
import os.path as pth

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64

from promus.core import git, ssh


def encrypt_to_file(msg, fname, keyfile):
    """Encrypt `msg` to the file `fname` using the key given by the
    path `keyfile`."""
    with open(keyfile, 'rb') as keyfp:
        keydata = keyfp.read()
    key = rsa.PrivateKey.load_pkcs1(keydata)
    msg = rsa.encrypt(msg.encode('utf-8'), key)
    with open(fname, 'wb') as msgfp:
        msgfp.write(msg)


def decrypt_from_file(fname, keyfile):
    """Decrypt a message in the file `fname` using the key given by
    the path `keyfile`"""
    with open(keyfile, 'rb') as keyfp:
        keydata = keyfp.read()
    key = rsa.PrivateKey.load_pkcs1(keydata)
    with open(fname, 'rb') as msgfp:
        msg = msgfp.read()
    return rsa.decrypt(msg, key).decode('utf-8')


def send_mail(send_to, subject, text, html, files=None):
    """Send an email. `send_to` must be a list of email address to
    which the email will be sent. You can email a `subject` as well
    as two versions of the email: text and html. You may optionally
    attach files by providing a list of them. """
    if not send_to:
        return
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'promus@%s' % socket.gethostname()
    msg['To'] = ','.join(send_to)

    msg.attach(MIMEText(text, 'plain'))
    htmlmsg = MIMEMultipart()
    htmlmsg.attach(MIMEText(html, 'html'))

    if files is None:
        files = []
    for file_ in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_, "rb").read())
        encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % pth.basename(file_))
        htmlmsg.attach(part)
    msg.attach(htmlmsg)
    server = git.config('host.smtpserver')
    conn = SMTP(server)
    conn.set_debuglevel(False)
    id_key, _ = ssh.get_keys()
    passfile = pth.expanduser('~/.promus/password.pass')
    password = decrypt_from_file(passfile, id_key)
    if password:
        conn.login(git.config('host.username'), password)
    try:
        conn.sendmail(git.config('host.email'), send_to, msg.as_string())
    finally:
        conn.close()
