# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import database
import entries
import notebooks
import utilities

class AdditionQueue:
    """
    Represents a queue of entries to be added to the database. Handles storing,
    validation, and writing of the entries.
    """

    def __init__(self, nid):
        self.entries = []
        self.history = []
        self.nid = nid
        self.ntype = notebooks.get_info(self.nid, "ntype")[0]

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

        if len(self.entries) >= 5:
            self.dump()

    def validatePages(self, entry):
        pass

    def showQueue(self):
        print "Queue: %r" % (self.entries)

    def showHistory(self):
        #TODO: A way to specify you only want to see the last x entries, like with tail
        print "Added: %r" % (self.history)
        self.showQueue()

    def dump(self):
        """
        Save queue to the database, then commit the changes. If there is
        nothing in the queue, do nothing.

        State change: Update self.entries with the new list.
        """

        if not self.entries:
            return

        for i in self.entries[:]:
            entry, pagenum = self.entries.pop(0)
            self.history.append((entry,pagenum))
            ntype, nnum = notebooks.get_info(self.nid, "ntype, nnum")
            entries.add_occurrence(entry, ntype, nnum, pagenum)

        database.connection.commit()

    def strike(self, number=1):
        """
        Remove the last item(s) from the queue, if the queue has any items.
        """
        #TODO: Catch in case user accidentally types e.g. "/strike 500"
        # create a termdisplay function called "warnyn" or um

        for i in range(number):
            if self.entries:
                print "Removed %s.\n" % (self.entries[-1][0]),
                del self.entries[-1]
            elif self.history:
                print "Removed %s (from history).\n" % (self.history[-1][0]),
                self.strike_from_history()
            else:
                print "Nothing more to be struck."
                break

    def strike_from_history(self):
        """
        Delete the last item from the history list, then remove it from said
        list.
        """

        entry, pagenum = self.history[-1]
        eid = entries.get_eid(entry)
        database.cursor.execute('DELETE FROM occurrences WHERE eid = ?'
                                   'AND page = ?', (eid, pagenum))
        if not entries.fetch_occurrences(eid): # no other occurrences
            entries.delete_entry(eid)

        self.history.pop()


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
            i = utilities.zero_pad(i, ntype)
            finishedPages.append(i)
        return finishedPages
    else:
        # single entry
        #TODO: zero-pad ranges
        page = utilities.zero_pad(page, ntype)
        return [page]

