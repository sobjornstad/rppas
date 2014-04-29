# -*- coding: utf-8 -*-
import db.database
import db.entries
import db.notebooks
import db.utilities

import config
import termdisplay

def screen():
    """
    Screen for adding entries to the list.

    We save every time the list reaches 6 elements, but only save the first
    five of them. This way, we always preserve the ability to undo at least one
    item (if it hasn't saved, we can undo an indefinite number up to before the
    save).
    """

    nid = getNotebook()
    if not nid:
        return

    print "Enter /help for information about adding commands."
    entries = []
    while True:
        print ""
        entry = termdisplay.ask_input("Entry:")

        if entry == "/help":
            print "Available commands:"
            print "/help   - show this help screen"
            print "/save   - save entries now"
            print "/show   - show entries in queue"
            print "/strike - remove previous entry"
            print "/quit   - stop adding entries"
        elif entry == "/save":
            entries = saveEntries(entries, nid)
        elif entry == "/show":
            print "Queue: %r" % entries
        elif entry == "/strike":
            if entries:
                print "Removed %s.\n" % (entries[-1][0])
                del entries[-1]
            else:
                print "Nothing to be struck."
        elif entry == "/quit":
            saveEntries(entries, nid, final=True)
            break
        else:
            page = termdisplay.ask_input("Page:", extended=True)
            ntype = db.notebooks.get_info(nid, "ntype")[0]
            pageList = processPages(page, ntype)
            for i in pageList:
                entries.append((entry,i))
            if len(entries) > 5:
                entries = saveEntries(entries, nid)

def processPages(page, ntype):
    """
    Split the pages entered into a list of pages (often only one, but several
    are possible as well). Make sure that all the pages are valid (if not,
    return False) and pad them with leading zeroes.

    Arguments: the string entered for pages and the ntype we're adding to
    (needed for zero padding). 
    Return: a list of strings to be added.
    """

    # Commas signify several occurrences of the entry, to be processed
    # separately, but a 'see FOO' entry might have commas and shouldn't
    # be split. This might break on a "see also," but we can't be perfect.
    if ',' in page and 'see' not in page:
        # more than one entry
        pages = page.split(',')
        finishedPages = []
        for i in pages:
            i = i.strip()
            i = db.utilities.zero_pad(i, ntype)
            finishedPages.append(i)
        return finishedPages
    else:
        # single entry
        page = db.utilities.zero_pad(page, ntype)
        return [page]

def saveEntries(entries, nid, final=False):
    """
    Given a list of recent entries and the nid for the notebook we're adding
    to, save them to the database. In order to maintain undoability, we don't
    save the very final entry to disk unless 'final=True' is set (used before
    quitting).

    Return the list that was passed in, with elements that were saved removed.
    """

    if not entries:
        return []

    if not final:
        lastEntry = entries.pop()

    for i in entries[:]:
        entry, pagenum = entries.pop()
        ntype, nnum = db.notebooks.get_info(nid, "ntype, nnum")
        db.entries.add_occurrence(entry, ntype, nnum, pagenum)

    db.database.connection.commit()
    if not final:
        return [lastEntry]
    else:
        return []

def getNotebook():
    """
    Ask user what notebook they want to add entries to and return the nid.
    Return None if the user entered a nonexistent (but valid) notebook.
    """

    print "\nWhat notebook do you want to add entries to?"
    while True:
        print ""
        ntype = termdisplay.ask_input("Type:")
        nnum = termdisplay.ask_input("Number:", extended=True)
        if ntype.upper() not in config.NOTEBOOK_TYPES:
            print "Invalid notebook type!"
            continue
        try: nnum = int(nnum)
        except:
            print "Invalid notebook number!"
            continue

        nid = db.notebooks.get_nid(ntype, nnum)
        if not nid:
            print "That notebook does not exist! Please create it first."
            raw_input("~ Strike any key to continue... ~")
            # allow creating it?
            return None
        return nid
