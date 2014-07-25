"""TeX utilities"""

import os
import promus.util as util
import promus.git as git


def gen_from_file(texfile, fname):
    """Generates a single file with the contents of the texfile (no
    includes)"""
    tmpf = open("%s.tex" % fname, 'w')
    for line in open("%s.tex" % texfile, 'r'):
        line = line.split('%')[0]
        pattern = '\input{'
        index = line.find(pattern)
        if index == -1:
            pattern = '\include{'
            index = line.find(pattern)
        if index != -1:
            end = line.find('}', index+1)
            inc_file = line[index+len(pattern):end]
            tmpf.write(line[:index])
            tmpf.write(open("%s.tex" % inc_file, 'r').read())
            tmpf.write(line[end+1:-1]+'\n')
        else:
            if line != '':
                tmpf.write(line)
                if line[-1] != '\n':
                    tmpf.write('\n')


def gen_from_git(texfile, fname, rev):
    """Generates a single tex file from the repository. """
    tmpf = open("%s.tex" % fname, 'w')
    lines, _, _ = util.exec_cmd("git show HEAD~%s:./%s.tex" % (rev,texfile))
    for line in lines.split('\n'):
        line = line.split('%')[0]
        pattern = '\input{'
        index = line.find(pattern)
        if index == -1:
            pattern = '\include{'
            index = line.find(pattern)
        if index != -1:
            end = line.find('}', index+1)
            inc_file = line[index+len(pattern):end]
            cmd = "git show HEAD~%s:./%s.tex" % (rev, inc_file)
            inc, _, _ = util.exec_cmd(cmd)
            tmpf.write(line[:index])
            tmpf.write(inc)
            tmpf.write(line[end+1:-1]+'\n')
        else:
            if line != '':
                tmpf.write(line)
                if line[-1] != '\n':
                    tmpf.write('\n')

def diff(prs, texfile):
    """Generates a pdf with the differences in the tex file texfile
    must be a string specifying the texfile. You may optionally
    specify which versions you wish to compare. For instance

        diff("mytexfile,0,2") # generates the diff between the current
                                  # version in storage with the version
                                  # 2 states ago
        diff("mytexfile,2") # differences between the current file you
                                # are editing and the version 2 states ago
        diff("mytexfile,3,4") # diff between 3 and 4
    
    -1: current file
    0: file in latest commit
    n: file in the last nth commit
    """
    tmp = texfile.split(",")
    texfile = tmp[0]
    version1 = "C"
    version2 = "0"
    if len(tmp) == 2:
        version2 = tmp[1]
    elif len(tmp) == 3:
        version1 = tmp[1]
        version2 = tmp[2]
    if version1 == "C":
        gen_from_file(texfile, "texfile.tmp1")
    else:
        gen_from_git(texfile, "texfile.tmp1", version1)
    if version2 == "C":
        gen_from_file(texfile, "texfile.tmp2")
    else:
        gen_from_git(texfile, "texfile.tmp2", version2)
    cmd = "latexdiff texfile.tmp1.tex texfile.tmp2.tex"
    ans, err, _ = util.exec_cmd(cmd)
    with open("%s-diff-%s-%s.tex" % (texfile, version1, version2), 'w') as tmpf:
        tmpf.write(ans)
    os.remove("texfile.tmp1.tex")
    os.remove("texfile.tmp2.tex")
    prs.dismiss("TEX.DIFF>> done...", 0)