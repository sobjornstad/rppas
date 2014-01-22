import backend
import exporter
import importer

def display_results(search, results):
    print "%s:" % search.upper(),
    for i in results:
        print "%s%i.%s" % (i[1][0], i[1][1], i[1][2]),
    print ""

def lookup_frontend():
    search = raw_input("> ")
    matches = backend.lookup(search)

    if not matches:
        print "%s: No results." % search.upper()
        return
    display_results(search, matches)

def search_frontend():
    search = raw_input("> ")
    print "Searching for %s..." % search.upper(),
    results, matches = backend.search_entries(search)

    if not results:
        print "no results."
        return
    else:
        print results

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
            results = backend.lookup(matches[entry][0])
            display_results(matches[entry][0], results)
        except KeyError:
            print "Invalid selection."
            return

def print_index():
    for entry in backend.dump_index():
        eid, name = entry
        matches = backend.fetch_occurrences(eid)

        print "%s:" % name.upper(),
        for i in matches:
            print "%s%i.%s" % (i[1][0], i[1][1], i[1][2]),
        print ""

def adder():
    #TODO: Make this resilient to user flubs.
    ntype = raw_input("What ntype to add to? ")
    nnum = int( raw_input("What nnum to add to? ") )

    while True:
        entry = raw_input("%s%i : " % (ntype, nnum))
        if entry == '': break
        page = int( raw_input("Page: ") )
        backend.add_entry(entry, ntype, nnum, page)
        backend.run_commit()

def export_index():
    filename = raw_input("Filename? ")
    exporter.export_index(filename)

def add_notebook():
    #TODO: Error checking
    #TODO: Better events editing
    ntype = raw_input("Type? ")
    nnum = int(raw_input("Number? "))
    opend = raw_input("Open date? ")
    closed = raw_input("Close date? ")
    events = raw_input("Events? ")
    backend.create_notebook(ntype, nnum, opend, closed, events)

def import_csv():
    filename = raw_input("Filename? ")
    importer.import_from_base(filename)

def main_menu():
    print "1) Print index"
    print "2) Search index"
    print "3) Lookup"
    print "4) Add to index"
    print "5) Add notebook"
    print "6) Export index to text"
    print "7) Import index from text"
    print "0) Quit"
    choice = raw_input("> ")

    if choice == '1':
        print_index()
    elif choice == '2':
        search_frontend()
    elif choice == '3':
        lookup_frontend()
    elif choice == '4':
        adder()
    elif choice == '5':
        add_notebook()
    elif choice == '6':
        export_index()
    elif choice == '7':
        importer.import_from_base('input.txt')
    else:
        backend.cleanup()

    main_menu()
