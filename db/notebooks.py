# -*- coding: utf-8 -*-

import database
import ui.termdisplay
import notebooks

def get_nid(ntype, nnum):
    """
    Find a notebook's nid from its type and number.
    
    Return values:
    - If successful, the nid.
    - If no notebooks match, 0.
    - If there is more than one match, -1 (this shouldn't be possible).
    """

    database.cursor.execute('SELECT nid FROM notebooks WHERE ntype=? AND nnum=?', \
                  (ntype, nnum))
    results = database.cursor.fetchall()
    if len(results) == 1:
        return results[0][0]
    elif len(results) == 0:
        return 0
    else:
        termdisplay.warn("Multiple notebooks with same type and number!")
        return -1

def create(ntype, nnum, opend, closed):
    """
    Create a notebook, given the parameters. If a notebook with the type and
    number already exists, do nothing and return False.

    To leave out a parameter, pass string NULL.

    Returns True if successfully created, False if notebook already existed.
    """

    # check if notebook exists already
    database.cursor.execute('SELECT nid FROM notebooks \
                    WHERE ntype = ? AND nnum = ?', (ntype, nnum))
    if database.cursor.fetchall():
        return False

    else: # good to go
        database.cursor.execute('INSERT INTO notebooks VALUES (null, ?, ?, ?, ?)',
                      (ntype, nnum, opend, closed))
        return True

def delete(nid):
    """Delete the notebook with specified nid from database. No return."""
    database.cursor.execute('DELETE FROM notebooks WHERE nid=?', (nid,))

def dump():
    """
    Return a list of tuples of all non-ID attributes of all notebooks, in the
    order (ntype, nnum, dopened, dclosed). This is intended to be used
    in displaying a list to the user, so nid is skipped; if you need it for a
    given notebook to do something with it, just run get_nid.

    Sort is by notebook type, then number.

    Similar to running get_notebook_info with all fields enabled, but
    automatically fetches the data for *all* notebooks instead of just one.
    """

    database.cursor.execute('SELECT ntype, nnum, dopened, dclosed FROM notebooks \
                    ORDER BY ntype, nnum')
    return database.cursor.fetchall()

def dump_dated(dopened, dclosed):
    """
    Like dump_notebooks, but requests only that subset of notebooks that were
    opened before a given date and closed after a given date.

    Specifically, the return is a list of tuples (ntype, nnum, dopened,
    dclosed).
    """

    database.cursor.execute('SELECT ntype, nnum, dopened, dclosed FROM notebooks \
                    WHERE dopened >= ? AND dclosed <= ? \
                    ORDER BY ntype, nnum', (dopened, dclosed))
    return database.cursor.fetchall()

def dump_open(dat):
    """
    Like dump_notebooks, but requests only that subset of notebooks that were
    open on a specific date.
    
    Specifically, the return is a list of tuples (ntype, nnum, dopened,
    dclosed).
    """

    database.cursor.execute('SELECT ntype, nnum, dopened, dclosed FROM notebooks \
                    WHERE dopened <= ? AND dclosed >= ? \
                    ORDER BY ntype, nnum', (dat, dat))
    return database.cursor.fetchall()

def get_info(nid, columns):
    """
    Get information about a notebook from its nid.

    For the "columns" argument, provide the DB column names; options are:
    - nid (but you already have that)
    - ntype
    - nnum
    - dopened
    - dclosed

    No validation of the provided column names is performed; make sure they're
    right before calling this function.

    Returns a tuple of the elements you asked for.
    """

    query_start = "SELECT "
    query_end = " FROM notebooks WHERE nid=%i" % nid
    query = query_start + columns + query_end

    database.cursor.execute(query)
    return database.cursor.fetchall()[0]

def rewrite_dates(nid, opend, closed):
    """Update the dates on notebook with specified nid. No return."""
    database.cursor.execute('UPDATE notebooks SET dopened=?, dclosed=? WHERE nid=?', \
                           (opend, closed, nid))

def adjacent(nid, direction):
    """
    Find the nid of the notebook numerically before or after the one of given
    nid. Will look for the next notebook if direction is zero or positive, the
    previous one if negative.

    Returns the nid of the adjacent notebook. If there is no adjacent notebook
    in that direction, quiet fail by returning the same nid passed.
    """

    ntype, nnum = notebooks.get_info(nid, "ntype, nnum")

    if direction >= 0:
        nnum += 1
    else:
        nnum -= 1

    if not notebooks.get_nid(ntype, nnum):
        return nid
    else:
        return notebooks.get_nid(ntype, nnum)
