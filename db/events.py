# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import ui.termdisplay
import database
import notebooks

class Event:
    def __init__(self, evid):
        self.evid = evid

    def getEvid(self):
        return self.evid

    def getNotebook(self):
        database.cursor.execute('SELECT nid FROM events WHERE evid = ?', \
                                (self.evid,))
        nid = database.cursor.fetchall()
        if not nid:
            return None
        else:
            return nid[0][0]

    def getText(self):
        database.cursor.execute('SELECT event FROM events WHERE evid = ?', \
                                (self.evid,))
        return database.cursor.fetchall()[0][0]

    def isSpecial(self):
        """
        Given an evid, determine if the associated event is considered a special or
        just a plain event.

        Return:
        - True if it is.
        - False if it isn't.
        - None if no event by that evid even exists.
        """

        database.cursor.execute('SELECT special FROM events WHERE evid = ?', \
                                (self.evid,))
        r = database.cursor.fetchall()
        if not r:
            return None
        elif r[0][0] == 1:
            return True
        else:
            return False

    def delete(self):
        """
        Delete the event with specified evid from database. No return.
        
        Does not commit changes in case you make a mistake and want to use
        rollback.
        """

        database.cursor.execute('DELETE FROM events WHERE evid=?',
                                (self.evid,))
        self.evid = 0

### EVENTS ###
def find_event(event, nid=None):
    """
    Given an event description and notebook, return an event object
    representing it, or None if there are no matches.

    There's the risk of having identical events across multiple notebooks and
    messing everything up, so when possible provide the nid. When it isn't
    provided, a little self-check will let the user select which one if
    necessary.
    """

    if nid:
        database.cursor.execute('SELECT evid FROM events WHERE event = ? AND nid = ?', (event,nid))
    else:
        database.cursor.execute('SELECT evid FROM events WHERE event = ?', (event,))
    evid = database.cursor.fetchall()
    if not evid:
        return None
    elif len(evid) > 1:
        print "Multiple events with the same name!"
        print "Notebooks:",
        for i in evid:
            ntype, nnum = notebooks.get_info(i[0], "ntype, nnum")
            print ntype + str(nnum) + ",",
        print "\b\b \n"
        while True:
            # only need number, as only CBs have events
            sel = termdisplay.ask_input("Select number of notebook to use:")

            # verify user's selection is actually right
            try: sel = int(sel)
            except ValueError: continue
            if (sel,) not in evid: continue
            else: return Event(sel)
            #TODO: ^^ this is buggy and returns the wrong event ^^
            # (puts in the nid, not the evid)
    else:
        return Event(evid[0][0])

def create(nid, event, isSpec=False):
    """
    Add *event* to the list of events for notebook *nid*. Optional argument
    isSpec specifies whether this is a "special event" -- i.e. associated with
    a particular date and written in the notebook's TOC in blue. This defaults
    to False.

    If the event already existed, this function does nothing and returns None.
    Otherwise, it returns an event object for the new event.
    """

    # make sure an event by this name and notebook doesn't already exist
    existing_event = find_event(event, nid)
    if existing_event:
        return None

    # one more than highest sequence number currently used in notebook's events
    database.cursor.execute('SELECT MAX(sequence) FROM events WHERE nid = ?', (nid,))
    try: seq = database.cursor.fetchall()[0][0] + 1
    except TypeError: seq = 1
    database.cursor.execute('INSERT INTO events VALUES (null, ?, ?, ?, ?)', (nid, event, isSpec, seq))
    return find_event(event, nid)

def reorder(ev1, ev2, nid):
    """
    Swaps the position numbers of two existing events in one notebook.

    Returns True if successful, false if evid(s) to update not found. (There is
    no need to return updated event objects; they are automatically updated
    since the only state variable is their nids.)
    """

    evids = (ev1.getEvid(), ev2.getEvid())
    seqs = []

    # I would make this one loop and use rollback(), but we're (sort of
    # hackishly) using rollback as an undo function, and doing so might lead a
    # user's other changes to be undone.
    for i in evids:
        database.cursor.execute('SELECT sequence FROM events WHERE evid = ?', (i,))
        seq = database.cursor.fetchall()
        if not seq:
            return False
        else:
            seqs.append(seq)

    seqs[0], seqs[1] = seqs[1], seqs[0]
    for i in range(len(evids)):
        database.cursor.execute('UPDATE events SET sequence=? WHERE evid=?', (seqs[i][0][0], evids[i]))
    return True

def fetch_in_notebook(nid):
    """
    Given a nid, find all events that take place in that notebook.

    Returns two lists of event objects, one for standards and one for specials,
    in the order they should be displayed.
    """

    database.cursor.execute('SELECT evid, special FROM events \
                    WHERE nid = ? ORDER BY sequence', (nid,))
    events, specials = [], []
    for i in database.cursor.fetchall():
        evid = i[0]
        isSpecial = i[1]
        if isSpecial:
            specials.append( Event(evid) )
        else:
            events.append( Event(evid) )

    return events, specials
