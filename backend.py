import sqlite3 as sqlite
import operator
import getpass
import signal
import sys
from config import PASSWORD, VALID_YEAR_RANGE, NOTEBOOK_TYPES, NOTEBOOK_SIZES

### FULL-DATABASE OPERATIONS ###

def access_control():
    """
    Ask for a password; should be run before initialize(). The DB is not
    encrypted and the password is stored in plaintext in config.py; this is
    just a fast way to keep out casual meddlers.

    While working on the program, you probably want to comment the call out at
    the bottom of this file.

    Exits the program if the password is not correct; no return.
    """

    pw = getpass.getpass("Password: ")
    if pw != PASSWORD:
        exit()

def sigint_handler(signal='', frame=''):
    """
    Run when Control-C is pressed at a menu or prompt. Runs the cleanup()
    routine to commit any stray transactions and exit nicely.

    Two optional arguments to accommodate signal.signal() as well as manual
    calling. No return.
    """

    print ""
    #print "Caught SIGINT, cleaning up..."
    cleanup()

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
    signal.signal(signal.SIGINT, sigint_handler) # for clean exit

def cleanup():
    """Commit any remaining changes and quit program. Obviously no return."""
    connection.commit()
    connection.close()
    sys.exit(0)


### NOTEBOOK OPERATIONS ###

def create_notebook(ntype, nnum, opend, closed):
    """
    Create a notebook, given the parameters. If a notebook with the type and
    number already exists, do nothing and return False.

    To leave out a parameter, pass string NULL.

    Returns True if successfully created, False if notebook already existed.
    """

    # check if notebook exists already
    cursor.execute('SELECT nid FROM notebooks \
                    WHERE ntype = ? AND nnum = ?', (ntype, nnum))
    if cursor.fetchall():
        return False

    else: # good to go
        cursor.execute('INSERT INTO notebooks VALUES (null, ?, ?, ?, ?)',
                      (ntype, nnum, opend, closed))
        return True

def rewrite_notebook_dates(nid, opend, closed):
    """Update the dates on notebook with specified nid. No return."""
    cursor.execute('UPDATE notebooks SET dopened=?, dclosed=? WHERE nid=?', \
                  (opend, closed, nid))

def delete_notebook(nid):
    """Delete the notebook with specified nid from database. No return."""
    cursor.execute('DELETE FROM notebooks WHERE nid=?', (nid,))

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
    order (ntype, nnum, dopened, dclosed). This is intended to be used
    in displaying a list to the user, so nid is skipped; if you need it for a
    given notebook to do something with it, just run get_nid.

    Sort is by notebook type, then number.

    Similar to running get_notebook_info with all fields enabled, but
    automatically fetches the data for *all* notebooks instead of just one.
    """

    cursor.execute('SELECT ntype, nnum, dopened, dclosed FROM notebooks \
                    ORDER BY ntype, nnum')
    return cursor.fetchall()

def dump_dated_notebooks(dopened, dclosed):
    """
    Like dump_notebooks, but requests only that subset of notebooks that were
    opened before a given date and closed after a given date.

    Specifically, the return is a list of tuples (ntype, nnum, dopened,
    dclosed).
    """

    cursor.execute('SELECT ntype, nnum, dopened, dclosed FROM notebooks \
                    WHERE dopened >= ? AND dclosed <= ? \
                    ORDER BY ntype, nnum', (dopened, dclosed))
    return cursor.fetchall()

def dump_open_notebooks(dat):
    """
    Like dump_notebooks, but requests only that subset of notebooks that were
    open on a specific date.
    
    Specifically, the return is a list of tuples (ntype, nnum, dopened,
    dclosed).
    """

    cursor.execute('SELECT ntype, nnum, dopened, dclosed FROM notebooks \
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

def check_exact_match(number, pageLow, pageHigh):
    """
    Determine if a match returned from nearby() query is actually a match.
    See the comment in the call in occurrences_around for why this happens.

    This function returns FALSE if argument 'number' (the number returned as a
    possibly valid entry by the database query) doesn't exactly match one of
    the numbers within margin. If number is a range, check both parts of it and
    allow if one of them matches.

    Return True if this match should be kept, False if it should be deleted.
    """

    acceptable_matches = number.split('-') # one-element list if not a range
    for i in acceptable_matches:
        for j in range(pageLow, pageHigh + 1):
            if str(j) == i:
                return True

    return False


def occurrences_around(ntype, nnum, page, margin=1):
    """
    Find other entries that are used on the same or a nearby page.

    Arguments:
    - ntype, nnum, page to look around. Page must be an int or we will crash.
    - (optional) Margin of nearby pages to look at as well. This will find
      ranges. Default value is 1.

    Returns a list of (page, entry) tuples sorted first numerically by page,
    then alphabetically by entry.
    """

    # find the nid of the notebook containing the entry we're looking at
    cursor.execute('SELECT nid FROM notebooks WHERE ntype = ? AND nnum= ?', (ntype, nnum))
    nid = cursor.fetchall()[0][0]

    # what page range are we looking at?
    pageLow = page - margin
    pageHigh = page + margin

    # find occurrences in same notebook with similar pages; surprisingly,
    # BETWEEN works perfectly on strings, and even finds ranges
    cursor.execute('SELECT eid, page FROM occurrences \
                    WHERE nid = ? AND page BETWEEN ? AND ?',\
                    (nid, pageLow, pageHigh))

    # now find what entries they belong to
    results = []
    counter = 0
    for i in cursor.fetchall():
        cursor.execute('SELECT name FROM entries WHERE eid = ?', (i[0],))
        results.append((i[1], cursor.fetchall()[0][0]))
        counter += 1

    # Some of these results might not be correct. For instance, searching
    # around '6' gets you 5, 6, 7 (correctly), but also 50-70. Remove any that
    # are wrong. (Leading zero enforcement should prevent this, but this should
    # head off any number of possible sort/between bugs.)
    for i in results[:]:
        if not check_exact_match(i[0], pageLow, pageHigh):
            results.remove(i)

    # I don't have the slightest idea what this is doing, but it implements the
    # sort I want: first by page number, then alphabetically (non-case-
    # sensitively) by entry
    # http://stackoverflow.com/questions/2494740/sort-a-list-of-tuples-without-case-sensitivity
    results.sort(key=lambda t : tuple(s.lower() if \
                        isinstance(s,basestring) else s for s in t))

    return results

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

def valid_date(date, unlimited_years=False):
    """
    Determine if a given date (YYYY-MM-DD string) is valid. Returns True if
    yes, False if problem. Will safely catch non-integer days.

    By default, will check to make sure the year could reasonably be within my
    lifetime or nearby (1990-2100). If this is not desired, pass
    unlimited_years = True.
    """

    month_days = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30,
                  7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

    # catch YYYY-MM-DD deviations
    date = date.split('-')
    try:
        year = date[0]
        month = date[1]
        day = date[2]
    except IndexError:
        return False
    if len(date) != 3: return False
    if len(year) != 4: return False
    if len(month) != 2: return False
    if len(day) != 2: return False

    # catch non-int-convertible values
    try:
        year, month, day = int(year), int(month), int(day)
    except ValueError:
        return False

    # catch out-of-bounds month and days
    if not 1 <= month <= 12: return False
    if not 1 <= day <= month_days[month]: return False

    # catch 2/29's on non-leap years
    if (month == 2) and (day == 29) and (year % 4): return False
    if (month == 2) and (day == 29) and (not year % 4):
        if (not year % 100) and (year % 400): return False

    # catch years obviously out of user's lifetime (configurable)
    # default 1990-2100
    if not unlimited_years:
        if not VALID_YEAR_RANGE[0] <= year <= VALID_YEAR_RANGE[1]:
            return False

    # if all these checks pass, the date should be valid
    return True

def validate_location(ntype, nnum, pagenum=None):
    """
    Check whether information the user has entered for a Nearby or When Was
    query can actually be used successfully to look up information.

    Requires ntype and nnum; pagenum is optional.

    Returns True if valid, False if invalid.
    """

    # make sure notebook exists
    if ntype not in NOTEBOOK_TYPES:
        return False
    if type(nnum) != int:
        return False
    if not get_nid(ntype, nnum):
        return False

    # check that page is positive and less than max for that notebook
    if pagenum: # optional test
        if type(pagenum) != int:
            return False
        if (pagenum < 1) or (pagenum > NOTEBOOK_SIZES[ntype]):
            return False

    return True

def zero_pad(i, ntype):
    """
    Add appropriate leading zeroes for an occurrence string. Determines whether
    one is needed based on the string length and the notebook type under
    consideration.

    Arguments: string to pad, notebook type.
    Return: padded string.
    """

    if len(i) == 2:
        if NOTEBOOK_SIZES[ntype] <= 99:
            pass
        elif NOTEBOOK_SIZES[ntype] <= 999:
            i = '0' + i
    elif len(i) == 1:
        assert ntype in NOTEBOOK_TYPES
        if NOTEBOOK_SIZES[ntype] <= 99:
            i = '0' + i
        elif NOTEBOOK_SIZES[ntype] <= 999:
            i = '00' + i
        else:
            termdisplay.warn("Your notebooks are very large. Unable to correctly pad page numbers with leading zeroes.")

    return i


def import_from_base(filename):
    """
    Import from my previous database format, a Base file (exported to TSV).

    Argument: name of the file to import. No return.
    """

    f = open(filename)
    for line in f:
        EID, ntype, nnum, page, entry = line.split('\t')
        nnum = int(nnum)
        entry = entry.strip()
        page = page.strip()

        create_notebook(ntype, nnum, "NULL", "NULL") # cancels if existing

        # Commas signify several occurrences of the entry, to be processed
        # separately, but a 'see FOO' entry might have commas and shouldn't
        # be split. This might break on a "see also," but we can't be perfect.
        if ',' in page and 'see' not in page:
            pages = page.split(',')
            for i in pages:
                i = i.strip()
                i = zero_pad(i, ntype)
                add_occurrence(entry, ntype, nnum, i)
        else: # single entry
            page = zero_pad(page, ntype)
            add_occurrence(entry, ntype, nnum, page)

    connection.commit()

### EVENTS ###
def get_evid(event, nid):
    """
    Given an event description and notebook, return the event ID, or None if it
    doesn't exist.
    """

    cursor.execute('SELECT evid FROM events WHERE event = ? AND nid = ?', (event,nid))
    evid = cursor.fetchall()
    if not evid:
        return None
    elif len(evid) > 1:
        # this is unlikely to happen, but just in case, say something
        termdisplay.warn("Multiple events in notebook " + str(nid) + " with the same name!")
    else:
        return evid[0][0]

def create_event(nid, event, isSpec=False):
    """
    Add *event* to the list of events for notebook *nid*. Optional argument
    isSpec specifies whether this is a "special event" -- i.e. associated with
    a particular date and written in the notebook's TOC in blue. This defaults
    to False.

    The event will not be created if it already exists. Returns False if it
    did, True if the event was added successfully.
    """

    # make sure an event by this name and notebook doesn't already exist
    if get_evid(event, nid):
        return False
    cursor.execute('INSERT INTO events VALUES (null, ?, ?, ?)', (nid, event, isSpec))
    return True

def rewrite_event(evid, nid, event, isSpec=False):
    """
    Works like create_event, but updates an existing event. Added first
    argument: the evid to overwrite. The evid provided must exist.

    Returns True if successful, false if evid to update not found.
    """

    cursor.execute('SELECT evid FROM events WHERE evid = ?', (evid,))
    if not cursor.fetchall():
        return False

    cursor.execute('UPDATE events SET nid=?, event=?, special=? WHERE evid=?', \
            (nid, event, isSpec, evid))
    return True

def delete_event(evid):
    """
    Delete the event with specified evid from database. No return.
    
    Does not commit changes in case you make a mistake and want to use
    rollback.
    """

    cursor.execute('DELETE FROM events WHERE evid=?', (evid,))

def fetch_notebook_events(nid):
    """
    Given a nid, find all events that take place in that notebook.

    Returns a tuple of two dictionaries: one for the standard events and one
    for those with isSpecial set ("specials"). Each dictionary has keys of the
    evids and values of the descriptions.
    """

    cursor.execute('SELECT evid, event, special FROM events WHERE nid = ?', (nid,))
    events, specials = {}, {}
    for i in cursor.fetchall():
        if i[2] == True:
            specials[i[0]] = i[1]
        else:
            events[i[0]] = i[1]

    return events, specials


##########

#access_control() # comment this out for testing
initialize()

if __name__ == "__main__":
    pass
    create_event(1, "Soren is alive.", False)
    rewrite_event(3, 1, "Soren is STILL alive!", True)
    print get_evid("Soren is alive.", 1)
    events, specials = fetch_notebook_events(1)
    print "events are:\n%r" % events
    print "specials are:\n%r" % specials

    cleanup()
