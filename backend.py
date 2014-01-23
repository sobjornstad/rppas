import sqlite3 as sqlite
import operator
import getpass

### FULL-DATABASE OPERATIONS ###

def access_control():
    """
    Ask for a password; should be run before initialize(). The DB is not
    encrypted and the password is stored in plaintext; this is just a fast way
    to keep out casual meddlers.

    While working on the program, you probably want to comment the call out at
    the bottom of this file.

    Exits the program if the password is not correct; no return.
    """

    pw = getpass.getpass("Password: ")
    if pw != 'Mauddie':
        exit()

def initialize():
    """
    Connect to the database; initialize backend module variables connection
    and cursor. Should be run when importing this module; no reason to do so
    thereafter.
    """

    global connection, cursor
    connection = sqlite.connect("records.db")
    connection.text_factory = str # fix for some weird Unicode error
    cursor = connection.cursor()

def cleanup():
    """Commit any remaining changes and quit program. Obviously no return."""
    connection.commit()
    connection.close()
    exit()


### NOTEBOOK OPERATIONS ###

def create_notebook(ntype, nnum, opend, closed, events):
    """
    Create a notebook, given the parameters. If a notebook with the type and
    number already exists, print error and do nothing further.

    To leave out a parameter, pass string NULL.

    Returns True if successfully created, False if notebook already existed.
    """

    # check if notebook exists already
    cursor.execute('SELECT nid FROM notebooks \
                    WHERE ntype = ? AND nnum = ?', (ntype, nnum))
    if cursor.fetchall():
        return False

    else: # good to go
        cursor.execute('INSERT INTO notebooks VALUES (null, ?, ?, ?, ?, ?)',
                      (ntype, nnum, opend, closed, events))
        return True

def rewrite_notebook_events(nid, events):
    """Update the events field on notebook with specified nid. No return."""
    cursor.execute('UPDATE notebooks SET events=? WHERE nid=?', (events, nid))
    connection.commit()

def rewrite_notebook_dates(nid, opend, closed):
    """Update the dates on notebook with specified nid. No return."""
    cursor.execute('UPDATE notebooks SET dopened=?, dclosed=? WHERE nid=?', \
                  (opend, closed, nid))
    connection.commit()

def delete_notebook(nid):
    """Delete the notebook with specified nid from database. No return."""
    cursor.execute('DELETE FROM notebooks WHERE nid=?', (nid))
    connection.commit()

def get_nid(ntype, nnum):
    """
    Find a notebook's nid from its type and number.
    
    Return values:
    - If successful, the nid.
    - If no notebooks match, 0.
    - If there is more than one match, -1 (this shouldn't be possible).
    """

    cursor.execute('SELECT nid FROM notebooks WHERE ntype=? AND nnum=?', \
                  (ntype, nnum))
    results = cursor.fetchall()
    if len(results) == 1:
        return results[0][0]
    elif len(results) == 0:
        return 0
    else:
        return -1

def dump_notebooks():
    """
    Return a list of tuples of all non-ID attributes of all notebooks, in the
    order (ntype, nnum, dopened, dclosed, events). This is intended to be used
    in displaying a list to the user, so nid is skipped; if you need it for a
    given notebook to do something with it, just run get_nid.

    Sort is by notebook type, then number.

    Similar to running get_notebook_info with all fields enabled, but
    automatically fetches the data for *all* notebooks instead of just one.
    """

    cursor.execute('SELECT ntype, nnum, dopened, dclosed, events FROM notebooks \
                    ORDER BY ntype, nnum')
    return cursor.fetchall()

def dump_dated_notebooks(dopened, dclosed):
    """
    Like dump_notebooks, but requests only that subset of notebooks that were
    opened before a given date and closed after a given date.

    Specifically, the return is a list of tuples (ntype, nnum, dopened,
    dclosed, events).
    """

    cursor.execute('SELECT ntype, nnum, dopened, dclosed, events FROM notebooks \
                    WHERE dopened >= ? AND dclosed <= ? \
                    ORDER BY ntype, nnum', (dopened, dclosed))
    return cursor.fetchall()

def dump_open_notebooks(dat):
    """
    Like dump_notebooks, but requests only that subset of notebooks that were
    open on a specific date.
    
    Specifically, the return is a list of tuples (ntype, nnum, dopened,
    dclosed, events).
    """

    cursor.execute('SELECT ntype, nnum, dopened, dclosed, events FROM notebooks \
                    WHERE dopened <= ? AND dclosed >= ? \
                    ORDER BY ntype, nnum', (dat, dat))
    return cursor.fetchall()

def get_notebook_info(nid, columns):
    """
    Get information about a notebook from its nid.

    For the "columns" argument, provide the DB column names; options are:
    - nid (but you already have that)
    - ntype
    - nnum
    - dopened
    - dclosed
    - events

    No validation of the provided column names is performed; make sure they're
    right before calling this function.

    Returns a tuple of the elements you asked for.
    """

    query_start = "SELECT "
    query_end = " FROM notebooks WHERE nid=%i" % nid
    query = query_start + columns + query_end

    cursor.execute(query)
    return cursor.fetchall()[0]


### ENTRY OPERATIONS ###

def get_entry_eid(entry):
    """Given an entry's name, return its eid, or None if entry does not exist."""

    cursor.execute('SELECT eid FROM entries WHERE name = ?;', (entry,))
    eid = cursor.fetchall()
    if eid:
        return eid[0][0]
    else:
        return None

def occurrences_around(ntype, nnum, page, margin=1):
    """
    Find other entries located on the same or a nearby page.

    Arguments:
    - ntype, nnum, page to look around.
    - (optional) Margin of nearby pages to look at as well, if an int is given.
      Surprisingly, this will find ranges, and can even search on ranges.
      Default value is 1.

    Returns a list of (page, entry) tuples sorted first numerically by page,
    then alphabetically by entry.
    """

    # find the nid of the notebook containing the entry we're looking at
    cursor.execute('SELECT nid FROM notebooks WHERE ntype = ? AND nnum= ?', (ntype, nnum))
    nid = cursor.fetchall()[0][0]

    # what page range are we looking at?
    try:
        pageLow = int(page) - margin
        pageHigh = int(page) + margin
    except ValueError:
        # if the user entered a non-int page (perhaps a range), just search that
        pageLow, pageHigh = page, page

    # find occurrences with similar pages; surprisingly, BETWEEN works
    # perfectly on strings, and even finds ranges
    cursor.execute('SELECT eid, page FROM occurrences \
                    WHERE nid = ? AND page BETWEEN ? AND ?',\
                    (nid, pageLow, pageHigh))

    # now find what entries they belong to
    results = {}
    counter = 0
    for i in cursor.fetchall():
        cursor.execute('SELECT name FROM entries WHERE eid = ?', (i[0],))
        results[counter] = (i[1], cursor.fetchall()[0][0])
        counter += 1

    # multi-step sort: put the dict into a list of tuples, sort by number, then
    #                  by non-case-sensitive alphabetical
    sort_step1 = sorted(results.iteritems(), key=operator.itemgetter(1))
    results_sorted = []
    for i in sort_step1:
        results_sorted.append(i[1])
    # I don't have the slightest idea what this is doing, but it works.
    # http://stackoverflow.com/questions/2494740/sort-a-list-of-tuples-without-case-sensitivity
    results_sorted.sort(key=lambda t : tuple(s.lower() if \
                        isinstance(s,basestring) else s for s in t))

    return results_sorted

def add_occurrence(entry, ntype, nnum, pagenum):
    """
    Create a new occurrence, adding the entry if it does not already exist.
    The arguments should be obvious from the declaration.
    
    This function does *not* commit the changes for performance reasons; the
    calling function should handle doing it when convenient so the changes are
    not lost if the program crashes.

    The notebook specified must exist.

    Return True if it works, False if the occurrence already existed.
    """

    #TODO: We should modify this to check for the notebook not existing

    # get notebook ID
    cursor.execute('SELECT nid FROM notebooks WHERE ntype = ? AND nnum = ?', (ntype, nnum))
    nid = cursor.fetchall()[0][0]

    # get entry eid if entry exists; add it if it does not
    eid = get_entry_eid(entry)
    if not eid:
        cursor.execute('INSERT INTO entries VALUES (null, ?)', (entry,))
        eid = get_entry_eid(entry) # now we can get it

    # enter occurrence for entry unless it already exists
    cursor.execute('SELECT oid FROM occurrences WHERE \
            page=? AND nid=? AND eid=?', (pagenum,nid,eid))
    if not cursor.fetchall():
        cursor.execute('INSERT INTO occurrences VALUES (null, ?, ?, ?)', (pagenum, nid, eid))
        return True
    else:
        return False

def fetch_occurrences(eid):
    """
    Given an EID, get occurrences that match it.

    Return occurrence locations in the form of a list of tuples 
    (ntype, nnum, page).
    """

    cursor.execute('SELECT occurrences.nid, occurrences.page FROM occurrences \
                    WHERE eid = ?', (eid,))

    # Loop over list of occurrences that reference entry. Store each match's ref
    # in a dictionary using a match_num ID used only here.
    matches = []
    for i in cursor.fetchall():
        nid, pagenum = i
        cursor.execute('SELECT notebooks.ntype, notebooks.nnum FROM notebooks \
                        WHERE nid = ?', (nid,))
        ntype, nnum = cursor.fetchall()[0]

        matches.append((ntype, nnum, pagenum))

    # sort in order placed: by type, notebook num, page num
    # unfortunately, does alphabetical sort on numbers in pagenums, as that field
    # must be a string because of ranges and parens and sees
    # we can mitigate this by requiring leading zeroes when adding
    matches.sort()
    return matches

def lookup(search):
    """
    Look up the occurrences of an entry given the name of the entry.

    Returns same format as fetch_occurrences(): a list of tuples
    (ntype, nnum, page). Return None if there are no matches.
    """

    eid = get_entry_eid(search)
    if not eid:
        return

    matches = fetch_occurrences(eid)
    return matches

def search_entries(search):
    """
    Given a search string, find entries containing that substring.

    Returns a dictionary:
    - KEYS: numerical IDs (to be displayed and used to select)
    - VALUES: entries (as strings)

    To look up occurrences for one of the entries, then, the user can enter a
    number and the program can pull out the text of the entry using the
    dictionary, then use get_entry_eid to find EIDs and look up occurrences by
    that.
    """

    search = "%" + search + "%"
    cursor.execute('SELECT name FROM entries \
                    WHERE name LIKE ? \
                    ORDER BY name', (search,))

    matches = {}
    matchnum = 1
    for match in cursor.fetchall():
        matches[matchnum] = match[0]
        matchnum += 1

    if not matches:
        return 0, None
    else:
        return len(matches), matches

def dump_index():
    """Return list of tuples of EID and name of all entries. Not currently used."""
    cursor.execute('SELECT eid, name FROM entries ORDER BY name')
    return cursor.fetchall()

##########

#access_control() # comment this out for testing
initialize()

if __name__ == "__main__":
    # testing area; not run in normal operation
    #print fetch_occurrences(6)
    occurrences_around('CB', 2, 5)
