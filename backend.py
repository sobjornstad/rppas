import sqlite3 as sqlite
import operator
import getpass
from functools import cmp_to_key
import locale

### FULL-DATABASE OPERATIONS ###

def access_control():
    """
    Ask for a password; should be run before initialize(). The DB is not
    encrypted and the password is stored in plaintext; this is just a fast way
    to keep out casual meddlers.

    While working on the program, you probably want to comment the call out at
    the bottom of this file.
    """

    pw = getpass.getpass("Password: ")
    if pw != 'Mauddie':
        exit()

def initialize():
    global connection, cursor
    connection = sqlite.connect("records.db")
    connection.text_factory = str # fix for some weird Unicode error
    cursor = connection.cursor()

def cleanup():
    connection.commit()
    exit()

def run_commit():
    # This is unnecessary; we should just run backend.connection.commit().
    connection.commit()


### NOTEBOOK OPERATIONS ###

def create_notebook(ntype, nnum, opend, closed, events):
    """
    Create a notebook, given the parameters. If a notebook with the type and
    number already exists, print error and do nothing further.
    
    To leave out a parameter, pass string NULL.
    """

    cursor.execute('SELECT nid FROM notebooks WHERE ntype = ? AND nnum = ?', (ntype, nnum))
    if cursor.fetchall():
        print "Notebook %s%i already exists!" % (ntype, nnum)
        return

    cursor.execute('INSERT INTO notebooks VALUES (null, ?, ?, ?, ?, ?)', (ntype, nnum, opend, closed, events))

def dump_notebooks():
    """Return a list of all attributes of all notebooks."""
    cursor.execute('SELECT ntype, nnum, dopened, dclosed, events FROM notebooks \
                    ORDER BY ntype, nnum') # or order by date once we have it
    return cursor.fetchall()

def dump_dated_notebooks(dopened, dclosed):
    """Like dump_notebooks, but requests only notebooks between two dates."""
    cursor.execute('SELECT ntype, nnum, dopened, dclosed, events FROM notebooks \
                    WHERE dopened > ? AND dclosed < ? \
                    ORDER BY ntype, nnum', (dopened, dclosed)) #once again, or order by dates
    return cursor.fetchall()

def dump_open_notebooks(dat):
    """Like dump_notebooks, but requests only notebooks open at a specific date."""
    cursor.execute('SELECT ntype, nnum, dopened, dclosed, events FROM notebooks \
                    WHERE dopened < ? AND dclosed > ? \
                    ORDER BY ntype, nnum', (dat, dat)) #once again, or order by dates
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

def rewrite_notebook_events(nid, events):
    cursor.execute('UPDATE notebooks SET events=? WHERE nid=?', (events, nid))
    connection.commit()

def rewrite_notebook_dates(nid, opend, closed):
    cursor.execute('UPDATE notebooks SET dopened=?, dclosed=? WHERE nid=?', \
                  (opend, closed, nid))
    connection.commit()

def delete_notebook(nid):
    cursor.execute('DELETE FROM notebooks WHERE nid=?', (nid))
    connection.commit()

def get_nid(ntype, nnum):
    """
    Find a notebook's nid from its type and number.
    
    Return:
    - If successful, the nid.
    - If no notebooks match, 0.
    - If there is more than one match, -1.
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


### ENTRY OPERATIONS ###

def get_entry_eid(entry):
    """Given an entry's name, return its eid."""
    cursor.execute('SELECT eid FROM entries WHERE name = ?;', (entry,))
    eid = cursor.fetchall()
    if eid:
        eid = eid[0][0]
        return eid
    else:
        return None

def occurrences_around(ntype, nnum, page, margin=1):
    """
    Find other entries located on the same or a nearby page.

    Arguments:
    - ntype, nnum, page to look around.
    - (optional) Margin of nearby pages to look at as well, if possible. If the
      page number of this entry is not a valid int, we won't be able to do it.
      I'm not sure why, but it will *find* ranges (but can't search on them). 
      Default value is 1.

    Returns a sorted list of page, entry tuples for display.
    """

    # find the nid of the notebook we're looking at
    cursor.execute('SELECT nid FROM notebooks WHERE ntype = ? AND nnum= ?', (ntype, nnum))
    nid = cursor.fetchall()[0][0]

    # should we accept nearby pages? by how much?
    try:
        # if the page is a simple int, we can give a fudge factor around it
        pageLow = int(page) - margin
        pageHigh = int(page) + margin
    except ValueError:
        # sometimes we'll only be able to give the exact page if not int-convertible
        pageLow, pageHigh = page, page

    # find occurrences with similar pages
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

def add_entry(entry, ntype, nnum, pagenum):
    """
    Create a new occurrence, adding the entry if it does not already exist.
    The arguments should be obvious from the declaration.
    
    This function does *not* commit the changes for performance reasons; the
    calling function should handle doing it when convenient so the changes are
    not lost if the program crashes.

    The notebook specified must exist.
    """

    #TODO: We should modify this to check for the notebook not existing

    # get notebook ID
    cursor.execute('SELECT nid FROM notebooks WHERE ntype = ? AND nnum = ?', (ntype, nnum))
    nid = cursor.fetchall()
    nid = nid[0][0]

    # get entry eid if it exists; add it if it does not
    eid = get_entry_eid(entry)
    if not eid:
        cursor.execute('INSERT INTO entries VALUES (null, ?)', (entry,))
        eid = get_entry_eid(entry) # now we can get it

    # enter occurrence for entry
    cursor.execute('SELECT oid FROM occurrences WHERE \
            page=? AND nid=? AND eid=?', (pagenum,nid,eid))
    if not cursor.fetchall():
        cursor.execute('INSERT INTO occurrences VALUES (null, ?, ?, ?)', (pagenum, nid, eid))
    else:
        print "Occurrence %s already exists." % entry.upper()

def fetch_occurrences(eid):
    """
    Given an EID, get occurrences that match it.

    Return occurrence locations in the form of a list of tuples:
        (sequential number, (ntype, nnum, page)).
    
    The sequential number is not meaningful and actually should probably be
    cleaned up here so every caller doesn't have to remove it. #TODO
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
    # must be a string for other reasons
    matches.sort()
    return matches


def lookup(search):
    """
    Look up the occurrences of an entry given the name of the entry.

    Returns same format as fetch_occurrences().
    """
    #TODO: Consider different formatting possibilities

    # find EID of entry to search for, find all occurrences that reference it
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
    - VALUES: strings representing the entries

    (To look up one of the entries, then, the user can enter a number and the
    program can pull out the text of the entry using the dictionary, then use
    get_entry_eid.)
    """
    search = "%" + search + "%"
    cursor.execute('SELECT name FROM entries \
                    WHERE name LIKE ? \
                    ORDER BY name', (search,))

                    #COLLATE NOCASE \
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
    print fetch_occurrences(6)
    # run any function you'd like, to test it
    #print dump_notebooks()
    #print occurrences_around('CB', 6, 12)
    #print get_notebook_info(2, "ntype, nid, dopened, events, dclosed, nnum")
    #rewrite_notebook_dates(2, "2013-04-01", "2013-05-04")

### old tests ###

#print_index()
#search("Maud")
#lookup("Bethamer, Maud")
#adder()

#exit()
#create_notebook("CB", 2)
#create_notebook("TB", 1)
#create_notebook("CB", 4)
#add_entry("Bethamer, Maud", "CB", 2, 24)
#add_entry("Bethamer, Maud", "CB", 2, 14)
#add_entry("Bethamer, Maud", "CB", 4, 14)
#add_entry("Bethamer, Maud", "CB", 4, 80)
#add_entry("Bethamer, Maud", "TB", 1, 220)
#add_entry("Bjornstad, Soren", "CB", 2, 50)
#add_entry("Bjornstad, Jennifer", "CB", 2, 50)
#lookup("Bethamer, Maud")
#lookup("Bjornstad, Soren")
#lookup("The Great Mouse")
