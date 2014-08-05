# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import re
import db.search
import db.entries
from db.utilities import unzero_pad

def formatEntries(elist):
    """Given a list of entries, format them for export."""
    #TODO: Progress bar

    ENTRY_STARTSTR = r"\item \textbf{"
    ENTRY_ENDSTR = r"}, "

    formatted = []
    e = sorted(elist.values(), key=lambda s: s.lower())
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
        print "found quotes"
        s = re.sub('\\\\textbf{(.*)""(.*)}', '\\\\textbf{``\\1"\\2}', s)

    return s

def printAllEntries():
    count, elist = db.search.Entries('')
    print "%i entries in database." % count
    entr = formatEntries(elist)

    DOC_STARTSTR = """\\documentclass{article}
\\usepackage[margin=0.5in]{geometry}
\\usepackage[utf8x]{inputenc}
\\usepackage[columns=3, indentunit=1.5em, columnsep=2em, font=small, justific=raggedright]{idxlayout}
\\begin{document}
\\begin{theindex}\n"""
    DOC_ENDSTR = """\\end{theindex}
\\end{document}\n"""

    with open('export.txt', 'w') as f:
        f.write(DOC_STARTSTR)
        f.writelines(entr)
        f.write(DOC_ENDSTR)
