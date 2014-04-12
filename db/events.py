# -*- coding: utf-8 -*-

import ui.termdisplay
import database
import notebooks

### EVENTS ###
def get_evid(event, nid=None):
    """
    Given an event description and notebook, return the event ID, or None if it
    doesn't exist.

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
            else: return sel
    else:
        return evid[0][0]

def which_notebook(evid):
    """
    Given an evid, find what notebook it is in.

    Argument: the evid. Return: the nid.
    """

    database.cursor.execute('SELECT nid FROM events WHERE evid = ?', (evid,))
    nid = database.cursor.fetchall()
    print nid
    if not nid:
        return None
    else:
        return nid[0][0]

def isSpecial(evid):
    """
    Given an evid, determine if the associated event is considered a special or
    just a plain event.

    Return:
    - True if it is.
    - False if it isn't.
    - None if no event by that evid even exists.
    """

    database.cursor.execute('SELECT special FROM events WHERE evid = ?', (evid,))
    r = database.cursor.fetchall()
    if not r:
        return None
    elif r[0][0] == 1:
        return True
    else:
        return False

def create(nid, event, isSpec=False):
    """
    Add *event* to the list of events for notebook *nid*. Optional argument
    isSpec specifies whether this is a "special event" -- i.e. associated with
    a particular date and written in the notebook's TOC in blue. This defaults
    to False.

    The event will not be created if it already exists. Returns False if it
    did, True if the event was added successfully.
    """

    # make sure an event by this name and notebook doesn't already exist
    if events.get_evid(event, nid):
        return False

    # one more than highest sequence number currently used in notebook's events
    database.cursor.execute('SELECT MAX(sequence) FROM events WHERE nid = ?', (nid,))
    try: seq = database.cursor.fetchall()[0][0] + 1
    except TypeError: seq = 1
    database.cursor.execute('INSERT INTO events VALUES (null, ?, ?, ?, ?)', (nid, event, isSpec, seq))
    return True

def reorder(evid1, evid2, nid):
    """
    Swaps the position numbers of two existing events in one notebook. The
    evids provided must exist.

    Returns True if successful, false if evid(s) to update not found.
    """

    evids = (evid1, evid2)
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

def delete(evid):
    """
    Delete the event with specified evid from database. No return.
    
    Does not commit changes in case you make a mistake and want to use
    rollback.
    """

    database.cursor.execute('DELETE FROM events WHERE evid=?', (evid,))

def fetch_in_notebook(nid):
    """
    Given a nid, find all events that take place in that notebook.

    Returns a tuple of two dictionaries and two lists. For the dictionaries:
    one for the standard events and one for those with isSpecial set
    ("specials"). Each dictionary has keys of the evids and values of the
    descriptions.

    The lists are the events and specials, in the order they should be
    displayed.
    """

    database.cursor.execute('SELECT evid, event, special FROM events \
                    WHERE nid = ? ORDER BY sequence', (nid,))
    events, specials = {}, {}
    eventsOrder, specialsOrder = [], []
    for i in database.cursor.fetchall():
        if i[2] == True:
            specials[i[0]] = i[1]
            specialsOrder.append(i[0])
        else:
            events[i[0]] = i[1]
            eventsOrder.append(i[0])

    return events, specials, eventsOrder, specialsOrder
