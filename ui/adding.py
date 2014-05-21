# -*- coding: utf-8 -*-
import db.database
import db.entries
import db.notebooks
import db.utilities

import config
import termdisplay

#TODO: Some of this should really go into the db side

class additionQueue:
    """
    Represents a queue of entries to be added to the database. Handles storing,
    validation, and writing of the entries.
    """

    def __init__(self, nid):
        self.entries = []
        self.history = []
        self.nid = nid
        self.ntype = db.notebooks.get_info(self.nid, "ntype")[0]

    def add(self, entry, page):
        """
        Add entry,page pairs to the database (passed as separate arguments).
        This method only updates the state of the object, not the actual
        database, though it is responsible for calling the dump method when
        the queue is "full."
        """

        pageList = processPages(page, self.ntype)
        for i in pageList:
            self.entries.append((entry,i))

        if len(self.entries) > 5:
            self.dump()

    def validatePages(self, entry):
        pass

    def showQueue(self):
        print "Queue: %r" % (self.entries)

    def showHistory(self):
        #TODO: A way to specify you only want to see the last x entries, like with tail
        print "Added: %r" % (self.history)
        self.showQueue()

    def dump(self, final=False):
        """
        Save queue to the database. In order to maintain undoability, we don't
        save the very final entry to disk unless 'final=True' is set (used before
        quitting). Then commit the changes.

        State change: Update self.entries with the new list.
        """

        if not self.entries:
            return
        if not final:
            lastEntry = self.entries.pop()

        for i in self.entries[:]:
            entry, pagenum = self.entries.pop()
            self.history.append((entry,pagenum))
            ntype, nnum = db.notebooks.get_info(self.nid, "ntype, nnum")
            db.entries.add_occurrence(entry, ntype, nnum, pagenum)

        db.database.connection.commit()
        if not final:
            self.entries = [lastEntry]
        else:
            self.entries = []

    def strike(self, number=1):
        """
        Remove the last item(s) from the queue, if the queue has any items.
        """

        for i in range(number):
            if self.entries:
                print "Removed %s.\n" % (self.entries[-1][0]),
                del self.entries[-1]
#            elif self.history:
#                # actually run the database delete command
#                # for this we need to add a delete_occurrence function
#                print "Removed %s.\n" % (self.history[-1][0]),
#                del self.history[-1]
            else:
                print "Nothing more to be struck."
                break


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
    else:
        queue = additionQueue(nid)

    print "Enter /help for information about adding commands."
    while True:
        print ""
        entry = termdisplay.ask_input("Entry:")

        if entry == "/help":
            print "Available commands:"
            print "/help       - show this help screen"
            print "/history    - show list of added entries"
            print "/save       - save entries now"
            print "/strike [#] - remove previous entry(ies)"
            print "/queue      - show unsaved entries"
            print "/quit       - stop adding entries"
            #TODO: Run a search from here (to edit or whatnot)
        elif entry == "/save":
            queue.dump()
        elif entry == "/queue":
            queue.showQueue()
        elif entry == "/history":
            queue.showHistory()
        elif entry.startswith("/strike"):
            if entry == "/strike": # no params
                queue.strike()
            else:
                parts = entry.split(' ')
                if len(parts) > 1:
                    try:
                        parts[1] = int(parts[1])
                    except ValueError: # not an int; ignore parameter
                        queue.strike()
                    else:
                        queue.strike(parts[1])
                else: # no parameter given
                    queue.strike()

        elif entry == "/quit":
            queue.dump(final=True)
            break
        else:
            page = termdisplay.ask_input("Page:", extended=True)
            queue.add(entry, page)

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
        #TODO: zero-pad ranges
        page = db.utilities.zero_pad(page, ntype)
        return [page]


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
