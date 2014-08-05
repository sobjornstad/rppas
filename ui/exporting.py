# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import os
import re
import subprocess
import sys
import tempfile

import db.search
import db.entries
from db.utilities import unzero_pad
from config import NOTEBOOK_TYPES
import termdisplay

def formatEntries(elist, count):
    """Given a list of entries, format them for export."""

    ENTRY_STARTSTR = r"\item \textbf{"
    ENTRY_ENDSTR = r"}, "

    formatted = []
    e = sorted(elist.values(), key=lambda s: s.lower())

    progress = 0
    perfifty = 0
    print "\nFormatting:",
    print "[                                                 ]",
    print '\b' * 51,
    sys.stdout.flush()

    for ename in e:
        oList = []
        occs = db.entries.fetch_occurrences(db.entries.get_eid(ename))
        for occ in occs:
            ntype, nnum, page = occ
            oList.append("%s%s.%s" % (ntype, nnum, unzero_pad(page)))
        occStr = ', '.join(oList)
        entryStr = ''.join([ENTRY_STARTSTR, ename, ENTRY_ENDSTR, occStr])
        entryStr = ''.join([entryStr, '\n'])
        entryStr = munge_latex(entryStr)
        formatted.append(entryStr)

        # progress update
        progress += 1
        if float(progress * 50 / count) > perfifty:
            perfifty = float(progress * 50 / count)
            sys.stdout.write(".")
            sys.stdout.flush()

    print "\n"
    return formatted

def munge_latex(s):
    "Escape characters reserved by LaTeX and format Markdown-like."

    # ampersands
    s = s.replace('&', '\\&')

    # italicize titles &c
    if "__" in s:
        s = re.sub("\\\\textbf{(.*)__(.*)}", "\\\\textbf{\emph{\\1}\\2}", s)
    # we could have typoes or other uses that result in single underscores
    s = s.replace('_', '\\textunderscore')

    # move opening quote to start of line
    if '""' in s:
        s = re.sub('\\\\textbf{(.*)""(.*)}', '\\\\textbf{``\\1"\\2}', s)

    # small-capify notebook names
    for nbuname in NOTEBOOK_TYPES:
        if nbuname in s:
            s = re.sub('%s' % nbuname, '{\\\\scshape %s\,}' % nbuname.lower(), s)

    # reformat 'see' entries with smallcaps and colons
    for redir in ['see', 'moved to', 'see also', 'also see']:
        if ''.join(['.', redir]) in s:
            s = re.sub(".%s (.*)" % redir, ": %s{\\\\scshape\ \\1}" % redir, s)
            repl = re.findall(": %s.*" % redir, s)
            repl = repl[0]
            repl.replace(": %s", "")
            s = s.replace(repl, repl.lower())

    # use en-dash in ranges; might grab a few wrong things; maybe worth it
    s = s.replace('-', '--')
    return s

def printAllEntries():
    count, elist = db.search.Entries('')
    entr = formatEntries(elist, count)

    DOC_STARTSTR = """\\documentclass{article}
\\usepackage[top=0.9in, bottom=0.8in, left=0.5in, right=0.5in, headsep=0in, landscape]{geometry}
\\usepackage[utf8x]{inputenc}
\\usepackage[columns=5, indentunit=0.75em, columnsep=0.5em, font=footnotesize, justific=raggedright, rule=0.5pt]{idxlayout}
\\usepackage[sc,osf]{mathpazo}
\\usepackage{fancyhdr}
\\fancyhf{}
\\pagestyle{fancy}
\\renewcommand{\\headrulewidth}{0.5pt}
\\fancyhead[LO,LE]{\\scshape The Complete Records Project Index}
\\fancyhead[CO,CE]{\\thepage}
\\fancyhead[RO,RE]{\\scshape \\today}
\\renewcommand{\\indexname}{\\vskip -0.25in}
\\begin{document}
\\begin{theindex}\n"""
    DOC_ENDSTR = """\\end{theindex}
\\end{document}\n"""

    # it would be good to delete the tmpdir we used at some point in the future
    tdir = tempfile.mkdtemp()
    oldcwd = os.getcwd()
    os.chdir(tdir)

    fnamebase = "index"
    tfile = os.path.join(tdir, '.'.join([fnamebase, 'tex']))
    with open(tfile, 'w') as f:
        f.write(DOC_STARTSTR)
        f.writelines(entr)
        f.write(DOC_ENDSTR)
    r = subprocess.call(['pdflatex', tfile])
    if r:
        termdisplay.warn("Error executing latex! Please see the error above.")
        return

    ofile = os.path.join(tdir, '.'.join([fnamebase, 'pdf']))
    if sys.platform.startswith('linux'):
        subprocess.call(["xdg-open", ofile])
    elif sys.platform == "darwin":
        os.system("open %s" % ofile)
    elif sys.platform == "win32":
        os.startfile(ofile)
    else:
        termdisplay.warn("Unable to automatically open the output. Please" \
                "browse manually to %s." % ofile)
    os.chdir(oldcwd)
