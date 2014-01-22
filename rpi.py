import sqlite3 as sqlite
import operator

def connect_db():
    global connection, cursor
    connection = sqlite.connect("records.db")
    cursor = connection.cursor()

def create_notebook(ntype, nnum):
    cursor.execute('SELECT nid FROM notebooks WHERE ntype = ? AND nnum = ?', (ntype, nnum))
    if cursor.fetchall:
        print "Notebook %s%i already exists!" % (ntype, nnum)
        return

    cursor.execute('INSERT INTO notebooks VALUES (null, ?, ?, ?, ?, ?)', (ntype, nnum, "2013-01-01", "2013-01-05", "foobar"))

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

    connection.commit()

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
    matches_sorted = sorted(matches.iteritems(), key=operator.itemgetter(1))
    return matches_sorted


def search_entry(search):
    #TODO: What if nothing found
    #TODO: Sort search results by chronology
    #TODO: Consider different formatting possibilities

    # find EID of entry to search for, find all occurrences that reference it
    eid = get_entry_eid(search)
    if not eid:
        print "%s: No results." % search.upper()
        return

    matches = fetch_occurrences(eid)

    print "%s:" % search.upper(),
    for i in matches:
        print "%s%i.%i" % (i[1][0], i[1][1], i[1][2]),
    print ""

    return

def inexact_search(search):
    print "Searching for %s..." % search.upper(),
    search = "*" + search + "*"
    cursor.execute('SELECT name FROM entries WHERE name GLOB ? ORDER BY name', (search,))

    matches = {}
    matchnum = 1
    for match in cursor.fetchall():
        matches[matchnum] = match
        matchnum += 1

    if not matches:
        print "\bno results."
        return
    else:
        print "\b%i results." % len(matches)
        for match in matches:
            print "%i: %s" % (match, matches[match][0].upper())

        entry = raw_input("Entry to look up or 0 to cancel: ")
        try:
            entry = int(entry)
        except ValueError:
            print "Invalid number."
            return
        else:
            if entry == 0:
                return
            try:
                search_entry(matches[entry][0])
            except KeyError:
                print "Invalid selection."
                return

def print_index():
    cursor.execute('SELECT eid, name FROM entries ORDER BY name')
    for entry in cursor.fetchall(): # use fetchall, fetch_occurrences steals the cursor
        eid, name = entry
        matches = fetch_occurrences(eid)

        print "%s:" % name.upper(),
        for i in matches:
            print "%s%i.%i" % (i[1][0], i[1][1], i[1][2]),
        print ""

def adder():
    #TODO: Make this resilient to user flubs.
    ntype = raw_input("What ntype to add to? ")
    nnum = int( raw_input("What nnum to add to? ") )

    while True:
        entry = raw_input("%s%i : " % (ntype, nnum))
        if entry == '': break
        page = int( raw_input("Page: ") )
        add_entry(entry, ntype, nnum, page)

def menu():
    print "1) Print index"
    print "2) Search index"
    print "3) Lookup"
    print "4) Add to index"
    print "5) Add notebook"
    print "0) Quit"
    choice = raw_input("> ")

    if choice == '1':
        print_index()
    elif choice == '2':
        inexact_search()
    elif choice == '3':
        search_entry()
    elif choice == '4':
        adder()
    elif choice == '5':
        create_notebook()
    else:
        exit()

    menu()




connect_db()
menu()

#print_index()
#inexact_search("Maud")
#search_entry("Bethamer, Maud")
#adder()

exit()
create_notebook("CB", 2)
create_notebook("TB", 1)
create_notebook("CB", 4)
add_entry("Bethamer, Maud", "CB", 2, 24)
add_entry("Bethamer, Maud", "CB", 2, 14)
add_entry("Bethamer, Maud", "CB", 4, 14)
add_entry("Bethamer, Maud", "CB", 4, 80)
add_entry("Bethamer, Maud", "TB", 1, 220)
add_entry("Bjornstad, Soren", "CB", 2, 50)
add_entry("Bjornstad, Jennifer", "CB", 2, 50)
search_entry("Bethamer, Maud")
search_entry("Bjornstad, Soren")
search_entry("The Great Mouse")
