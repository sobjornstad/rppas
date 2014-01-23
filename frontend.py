import termdisplay
import backend
from termdisplay import getch

def lookup_by_number(results):
    """
    Called after a search to ask for input and look up an item by number.
    
    This is separate from lookup_action because originally I had planned that
    you could initiate a straight lookup from the main menu, which would need a
    different by_number function but could use the same lookup_action function.
    You can no longer do this, but in case of future changes that permit
    lookups from different places, I'm leaving the functions divided.
    """

    index = termdisplay.ask_input("Lookup:")
    try:
        index = int(index)
    except ValueError:
        # maybe they typed the word instead; if not, they'll be told no matches
        lookup_action(index)
    else:
        # lookup by number
        lookup_action(results[index])

def lookup_action(search):
    """
    Find the entry being looked up (by lookup_by_number) and print out its
    occurrences.
    """

    matches = backend.lookup(search)

    if matches:
        print termdisplay.moveCodes.UP1 + termdisplay.colors.WHITE + \
                search + ":" + termdisplay.colors.ENDC,

        termlen = len(search) # to know how far to skip when breaking a line
        loopcount = 0
        # 2 is for chars already there (space); 5 is a buffer I don't understand.
        # It uses 12 when reset. I also don't understand this -- but they need
        # different values for some reason, and I don't see anything I did wrong.
        charcount = termlen + 2 + 5

        for i in matches:
            charcount += len("%s%i.%s" % (i[0], i[1], i[2]))
            if charcount > termdisplay.SCREEN_WIDTH:
                print '\b,\n ' + ' ' * termlen,
                loopcount = 0
                charcount = termlen + 2 + 12

            formatStr = termdisplay.colors.ENDC + "%s" + \
                        termdisplay.colors.GREEN + "%i" + \
                        termdisplay.colors.BLUE + ".%s" + \
                        termdisplay.colors.ENDC
            if loopcount == 0:
                print formatStr % (i[0], i[1], i[2]),
            else:
                print "\b, " + formatStr % (i[0], i[1], i[2]),

            charcount += 2 # for the comma and space
            loopcount += 1
    else:
        # should only happen when manual lookup by entering name
        print "No results."

    print ""
    termdisplay.entry_square()

def nearby():
    """
    Option from the search screen that allows the user to find other index
    entries used for an occurrence's page and nearby pages.

    No arguments; all requisite information is input within the function.
    """

    print ""
    ntype = termdisplay.ask_input("Nearby type:")
    nnum  = termdisplay.ask_input("        num:", extended=True)
    page  = termdisplay.ask_input("        page:", extended=True)

    results = backend.occurrences_around(ntype, nnum, page)

    formatStr = termdisplay.colors.GREEN + "%s%i" + \
                termdisplay.colors.ENDC + '.' + \
                termdisplay.colors.BLUE + "%s\t" + \
                termdisplay.colors.WHITE + "%s" + \
                termdisplay.colors.ENDC

    for i in results:
        print formatStr % (ntype, int(nnum), i[0], i[1])

    termdisplay.entry_square()

def when_was():
    """
    Option from the search screen to find the date a notebook was open, so that
    you can tell roughly when a given occurrence was written (useful for CB,
    probably not too much for other types).

    No arguments; all requisite information is input within the function.
    """

    print ""
    ntype = termdisplay.ask_input("When was type:")
    print termdisplay.moveCodes.UP1 + termdisplay.moveCodes.UP1
    nnum  = termdisplay.ask_input("          num:")
    nid = backend.get_nid(ntype, nnum)
    #also add events
    dopened, dclosed = backend.get_notebook_info(nid, "dopened, dclosed")

    print "That happened between %s and %s." % (dopened, dclosed)
    termdisplay.entry_square()

def search_screen():
    """
    Screen that allows the user to search for index entries matching a query,
    then optionally run a lookup, When was, or Nearby.
    """

    termdisplay.print_title()
    search = termdisplay.ask_input("Search:")
    results, matches = backend.search_entries(search)
    if matches:
        for i in matches:
            print "%i:\t%s" % (i, matches[i])
    else:
        print "No results."

    keys = ['L', 'S', 'N', 'W', 'Q']
    commands = {'L':'Lookup', 'S':'Search again', 'N':'Nearby',
                'W':'When was', 'Q':'Quit'}
    termdisplay.print_commands(keys, commands, '')
    termdisplay.entry_square()

    while True:
        c = getch()
        if c == 'l':
            print ""
            lookup_by_number(matches)
        elif c == 's':
            r = search_screen()
            if r == 'break':
                return 'break' # see below comment on 'q'
        elif c == 'w':
            when_was()
        elif c == 'n':
            nearby()
        elif c == 'q':
            # even if we run search several times, we only want to press q once
            return 'break'
        elif c in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # simply look up that item; last line of the lookup_by_number fn
            print ""
            lookup_action(matches[int(c)])
        else:
            print '\b!\b',
            continue

def list_notebooks():
    """
    Screen to display a list of notebooks, with or without filters. All
    filtering and editing is done from within this screen.
    """

    # start with no filters
    dopened = None
    dclosed = None
    dat = None
    filtered = None

    while True:
        termdisplay.print_title()
        if filtered == 'filterRange':
            print "Showing notebooks opened after %s and closed before %s." \
                    % (dopened, dclosed)
        elif filtered == 'openAt':
            print "Showing notebooks open on %s." \
                    % (dat)

        formatStr = termdisplay.colors.GREEN + "%s\t" + \
                    termdisplay.colors.BLUE + "%s\t" + \
                    termdisplay.colors.RED + "%s" + \
                    termdisplay.colors.ENDC
        print formatStr % ("Book", "Open Date", "Close Date")

        # filters?
        if filtered == 'filterRange':
            nlist = backend.dump_dated_notebooks(dopened, dclosed)
        elif filtered == 'openAt':
            nlist = backend.dump_open_notebooks(dat)
        else:
            nlist = backend.dump_notebooks()

        if not nlist:
            print "(no results)"
        for i in nlist:
            print formatStr % ((i[0] + str(i[1])), i[2], i[3])

        keys = ['E', 'F', 'O', 'C', 'V', 'Q']
        commands = {'E':'Edit', 'F': 'Filter', 'O':'Open at time',
                    'C': 'Clear filter', 'V': 'Events', 'Q':'Quit'}
        termdisplay.print_commands(keys, commands, '')
        termdisplay.entry_square()

        c = getch()
        if c == 'e':
            print ""
            r = edit_notebook()
            if r == 'break':
                return 'break' # see below comment on 'q'
        elif c == 'f':
            print ""
            dopened = termdisplay.ask_input("Opened after:")
            dclosed = termdisplay.ask_input("Closed before:", extended=True)
            filtered = 'filterRange'
        elif c == 'o':
            print ""
            dat = termdisplay.ask_input("Open at:")
            filtered = 'openAt'
        elif c == 'c':
            dopened, dclosed, dat, filtered = None, None, None, None
        elif c == 'q':
            return 'break'

def edit_notebook():
    """
    Edit the dates a notebook was open. Gets information within the function
    and returns nothing.

    Later, should also edit the events. We don't have code to handle events
    anywhere yet.
    """

    ntype = termdisplay.ask_input("Type to edit:")
    nnum = termdisplay.ask_input("Number to edit:", extended=True)

    nid = backend.get_nid(ntype, nnum)
    if nid == 0:
        print "Error -- no matches."
        termdisplay.entry_square()
        getch()
        return

    dopened, dclosed = backend.get_notebook_info(nid, "dopened, dclosed")
    nopen = termdisplay.ask_input("Open date [%s]:" % dopened, extended=True)
    nclose = termdisplay.ask_input("Close date [%s]:" % dclosed, extended=True)
    # validation of dates would be a good thing

    backend.rewrite_notebook_dates(nid, nopen, nclose)

def notebooks_screen():
    """
    Screen to allow listing and adding notebooks. Maybe something else later?
    """

    keys = ['L', 'A', 'Q']
    commands = {'L':'List notebooks',
                'A':'Add notebook',
                'Q':'Quit',
               }

    while True:
        termdisplay.print_title()
        termdisplay.print_commands(keys, commands, '  Notebooks')
        termdisplay.entry_square()
        c = getch()

        if c == 'l':
            list_notebooks()
        elif c == 'a':
            add_notebook()
        elif c == 'q':
            break
        else:
            continue

def main_screen():
    """
    Screen to select other screens. If you're working on this and aren't
    familiar with the concept of a main menu, get out.
    """

    keys = ['S', 'P', 'E', 'N', 'I', 'X', 'Q']
    commands = {'S':'Search',
                'P':'Print Index',
                'Q':'Quit',
                'N':'Notebooks',
                'E':'Edit Entries',
                'X':'Export',
                'I':'Import',
               }

    while True:
        termdisplay.print_title()
        termdisplay.print_commands(keys, commands, '  Main')
        termdisplay.entry_square()
        c = getch()

        if c == 's':
            search_screen()
        elif c == 'n':
            notebooks_screen()
        elif c == 'q' or c == '\x03': # ctrl-c
            backend.cleanup()
        else:
            continue

if __name__ == "__main__":
    print "Please run init.py to start the Indexer."
