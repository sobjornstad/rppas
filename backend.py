import sqlite3 as sqlite
import operator

### FULL-DATABASE OPERATIONS ###

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
    cursor.execute('SELECT eid FROM entries WHERE name = ?;', (entry,))
    eid = cursor.fetchall()
    if eid:
        eid = eid[0][0]
        return eid
    else:
        return None

def add_entry(entry, ntype, nnum, pagenum):
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
    # Given an EID, get occurrences that match it.

    cursor.execute('SELECT occurrences.nid, occurrences.page FROM occurrences \
                    WHERE eid = ?', (eid,))

    # Loop over list of occurrences that reference entry. Store each match's ref
    # in a dictionary using a match_num ID used only here.
    matches = {}
    match_num = 1
    for i in cursor.fetchall():
        nid, pagenum = i
        cursor.execute('SELECT notebooks.ntype, notebooks.nnum FROM notebooks \
                        WHERE nid = ?', (nid,))
        ntype, nnum = cursor.fetchall()[0]

        matches[match_num] = (ntype, nnum, pagenum)
        match_num += 1

    # sort in order placed: by type, notebook num, page num
    # unfortunately, does alphabetical sort on numbers in pagenums, as that field
    # must be a string for other reasons
    matches_sorted = sorted(matches.iteritems(), key=operator.itemgetter(1))
    return matches_sorted


def lookup(search):
    #TODO: What if nothing found
    #TODO: Consider different formatting possibilities

    # find EID of entry to search for, find all occurrences that reference it
    eid = get_entry_eid(search)
    if not eid:
        return

    matches = fetch_occurrences(eid)
    return matches

def search_entries(search):
    search = "%" + search + "%"
    cursor.execute('SELECT name FROM entries \
                    WHERE name LIKE ? \
                    ORDER BY name', (search,))

                    #COLLATE NOCASE \
    matches = {}
    matchnum = 1
    for match in cursor.fetchall():
        matches[matchnum] = match
        matchnum += 1

    if not matches:
        return 0, None
    else:
        return len(matches), matches

def dump_index():
    cursor.execute('SELECT eid, name FROM entries ORDER BY name')
    return cursor.fetchall()

##########

initialize()
if __name__ == "__main__":
    # run any function you'd like, to test it
    print dump_notebooks()
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
