"""Paster"""

from os.path import dirname, exists
import promus.util as util


def paste(prs, name):
    "Paste a template to current location. "
    tmp = dirname(__file__)
    if exists('%s/%s' % (tmp, name)):
        util.exec_cmd('cp -r %s/%s/* ./' % (tmp, name), True)
    else:
        prs.dismiss("PASTE>> no template found...", 1)
    prs.dismiss("PASTE>> done...", 0)
