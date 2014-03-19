# -*- coding: utf-8 -*-

import termdisplay
import backend
from termdisplay import getch
import config
from time import sleep

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
        # lookup by number; make sure it's a value that was in the results
        if index > len(results):
            print "Invalid lookup number."
            return
        else:
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
                # ntype, nnum, pagenum
                print formatStr % (i[0], i[1], i[2]),
            else:
                print "\b, " + formatStr % (i[0], i[1], i[2]),

            charcount += 2 # for the comma and space
            loopcount += 1
    else:
        print "No results."

    print ""

def nearby():
    """
    Option from the search screen that allows the user to find other index
    entries used for an occurrence's page and nearby pages.

    No arguments; all requisite information is input within the function.
    """

    while True:
        print ""
        ntype = termdisplay.ask_input("Nearby type:")
        nnum  = termdisplay.ask_input("        num:", extended=True)
        page  = termdisplay.ask_input("       page:", extended=True)
        try:
            nnum, page = int(nnum), int(page)
        except ValueError:
            print "Invalid entry!"
            continue
        if backend.validate_location(ntype, nnum, page):
            break
        else:
            print "Invalid entry!"

    results = backend.occurrences_around(ntype, nnum, int(page))

    formatStr = termdisplay.colors.GREEN + "%s%i" + \
                termdisplay.colors.ENDC + '.' + \
                termdisplay.colors.BLUE + "%s\t" + \
                termdisplay.colors.WHITE + "%s" + \
                termdisplay.colors.ENDC

    #TODO: Ranges can cause tabbing to look ugly
    if results:
        for i in results:
            print formatStr % (ntype, int(nnum), i[0], i[1])
    else:
        print "No results."

def when_was():
    """
    Option from the search screen to find the date a notebook was open, so that
    you can tell roughly when a given occurrence was written (useful for CB,
    probably not too much for other types).

    No arguments; all requisite information is input within the function.
    """

    while True:
        print ""
        ntype = termdisplay.ask_input("When was type:")
        nnum  = termdisplay.ask_input("          num:", extended=True)
        try:
            nnum = int(nnum)
        except ValueError:
            print "Invalid entry!"
            continue
        if backend.validate_location(ntype, nnum):
            break
        else:
            print "Invalid entry!"

    nid = backend.get_nid(ntype, nnum)
    events_screen(ntype, nnum)

def search_screen(search=None):
    """
    Screen that allows the user to search for index entries matching a query,
    then optionally run a lookup, When was, or Nearby.

    Optional argument: the search to run. Otherwise the user will be asked.
    """

    termdisplay.print_title()
    if not search:
        search = termdisplay.ask_input("Search:")
    else:
        termdisplay.fake_input("Search:", search)
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

    while True:
        termdisplay.entry_square()
        c = getch().lower()
        if c == 'l':
            print ""
            lookup_by_number(matches)
        elif c == 's':
            r = search_screen()
            if r == 'break':
                return 'break' # see below comment on 'q'
        elif c == 'w':
            when_was()
            r = search_screen(search)
            if r == 'break':
                return 'break' # see below comment on 'q'
        elif c == 'n':
            nearby()
        elif c == 'q':
            # even if we run search several times, we only want to press q once
            return 'break'
        elif c == '\x03': # ctrl-c
            backend.sigint_handler()
        elif c in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # simply look up that item; equivalent to the last lines of the
            # lookup_by_number() function
            print ""
            try:
                c = int(c)
            except:
                print "Invalid lookup number."
            if c > len(matches):
                print "Invalid lookup number."
            else:
                lookup_action(matches[c])
        else:
            print ""
            continue

def add_event(nid):
    event = termdisplay.ask_input("Event name:", extended=True)
    while True:
        isSpecial = termdisplay.ask_input("Special? (y/n):", extended=True)
        if isSpecial.lower() == 'y':
            isSpecial = True
            break
        elif isSpecial.lower() == 'n':
            isSpecial = False
            break
        else:
            print "Please type 'y' or 'n'.\n"

    ok = backend.create_event(nid, event, isSpecial)
    if not ok:
        print "Whoops, that event already exists!"
        termdisplay.entry_square()
        getch()

def delete_event(events, specials):
    """
    Ask for the key number to delete and remove it from the database.

    Arguments: The events and specials dictionaries storing the current state
               of events (no pun intended).
    Return: None.
    """

    events.update(specials)

    while True:
        todel = termdisplay.ask_input("Number to delete:")
        try:
            todel = int(todel)
        except ValueError:
            print "Enter the number of the item to delete."
        else:
            break
    evid_todel = events[todel][0]
    backend.delete_event(evid_todel)

def events_screen(ntype=None, nnum=None):
    """
    Screen that allows the user to look at and modify events in a selected
    notebook.

    Optional arguments specify the notebook type and number to show; if not
    specified, the user will be asked which one to look at.
    """

    first = True # clear screen only when switching books; 
                 # keep the table of books displayed the first time
    while True:
        if first:
            first = False
            print ""
        else:
            termdisplay.print_title()

        if not (ntype and nnum):
            ntype = termdisplay.ask_input("Type to view:")
            nnum = termdisplay.ask_input("Number to view:", extended=True)

        nid = backend.get_nid(ntype, nnum)
        if nid == 0:
            print "Nonexistent notebook, please try again."
            termdisplay.entry_square()
            getch()
        else:
            break

    while True:
        termdisplay.print_title()
        dopened, dclosed = backend.get_notebook_info(nid, "dopened, dclosed")
        events, specials = backend.fetch_notebook_events(nid)

        # switch to using a user-friendly numeric listing, but save the nid
        counter = 1
        newEvents, newSpecials = {}, {}
        for i in events:
            newEvents[counter] = (i, events[i])
            counter += 1
        for i in specials:
            newSpecials[counter] = (i, specials[i])
            counter += 1
        events, specials = newEvents, newSpecials

        # output list of events
        #TODO: What to do if the event name is too long to fit on the line comfortably
        print termdisplay.center("Events for %s%s%s%s" % (
            termdisplay.colors.GREEN, ntype, nnum, termdisplay.colors.ENDC))
        print termdisplay.center("  %s%s%s – %s%s%s" % (
            termdisplay.colors.WHITE, dopened, termdisplay.colors.RED,
            termdisplay.colors.WHITE, dclosed, termdisplay.colors.ENDC))

        print termdisplay.colors.BLUE + "\nEvents:" + termdisplay.colors.ENDC
        for i in events:
            print "%i:\t%s" % (i, events[i][1])
        print termdisplay.colors.BLUE + "\nSpecials:" + termdisplay.colors.ENDC
        for i in specials:
            print "%i:\t%s" % (i, specials[i][1])

        keys = ['A', 'D', 'S', 'U', 'B', 'Q']
        commands = {'A':'Add', 'D':'Delete', 'S':'Save changes',
                    'U':'Undo changes', 'B':'Change book', 'Q':'Quit'}
        termdisplay.print_commands(keys, commands, '')

        termdisplay.entry_square()
        c = getch().lower()
        if c == 'a':
            print ""
            add_event(nid)
        elif c == 'd':
            print ""
            delete_event(events, specials)
        elif c == 's':
            backend.connection.commit()
            print "\b\b\bSaved."
            sleep(0.5)
        elif c == 'u':
            backend.connection.rollback()
            print "\b\b\b\bUndone."
            sleep(0.5)
        elif c == 'b':
            r = events_screen()
            if r == 'break':
                return 'break' # see below comment on 'q'
        elif c == 'q':
            # even if we run search several times, we only want to press q once
            return 'break'
        elif c == '\x03': # ctrl-c
            backend.sigint_handler()
        else:
            print ""
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

        c = getch().lower()
        if c == 'e':
            print ""
            r = edit_notebook()
            if r == 'break':
                return 'break' # see below comment on 'q'
        elif c == 'f':
            while True:
                print ""
                dopened = termdisplay.ask_input("Opened after:")
                dclosed = termdisplay.ask_input("Closed before:", extended=True)
                if backend.valid_date(dopened) and backend.valid_date(dclosed):
                    break
                else:
                    print "Invalid date!"

            filtered = 'filterRange'
        elif c == 'o':
            while True:
                print ""
                dat = termdisplay.ask_input("Open at:")
                if backend.valid_date(dat):
                    break
                else:
                    print "Invalid date!"
            filtered = 'openAt'
        elif c == 'c':
            dopened, dclosed, dat, filtered = None, None, None, None
        elif c == 'v':
            events_screen()
        elif c == 'q':
            return 'break'
        elif c == '\x03': # ctrl-c
            backend.sigint_handler()

def add_notebook():
    """
    Create a new notebook. No arguments, no return.
    """

    while True:
        print ""
        ntype = termdisplay.ask_input("Type to add:")
        if ntype not in config.NOTEBOOK_TYPES:
            print "Invalid notebook type!"
        else:
            break

    while True:
        nnum = termdisplay.ask_input("Number to add:", extended=True)
        nid = backend.get_nid(ntype, nnum)
        if nid != 0:
            print "Notebook already exists!"
        else:
            break

    while True:
        dopened = termdisplay.ask_input("Date opened:", extended=True)
        dclosed = termdisplay.ask_input("Date closed:", extended=True)
        if not (backend.valid_date(dopened) and backend.valid_date(dclosed)):
            print "Invalid date(s)!"
            print ""
        elif dopened > dclosed:
            print "Specified open date is after close date!"
            print ""
        else:
            break

    backend.create_notebook(ntype, nnum, dopened, dclosed)
    backend.connection.commit()

def edit_notebook():
    """
    Edit the dates a notebook was open. Gets information within the function
    and returns nothing.
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
    while True:
        nopen = termdisplay.ask_input("Open date [%s]:" % dopened, extended=True)
        nclose = termdisplay.ask_input("Close date [%s]:" % dclosed, extended=True)

        # use current as defaults (bracketed)
        if not nopen:
            nopen = dopened
        if not nclose:
            nclose = dclosed

        # make sure dates are valid
        if not backend.valid_date(nopen) and backend.valid_date(nclose):
            print "Invalid date(s). Try again.\n"
        elif nopen > nclose:
            print "Specified open date is after close date! Try again.\n"
        else:
            break

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
        c = getch().lower()

        if c == 'l':
            list_notebooks()
        elif c == 'a':
            add_notebook()
        elif c == 'q':
            break
        elif c == '\x03': # ctrl-c
            backend.sigint_handler()
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
        c = getch().lower()

        if c == 's':
            search_screen()
        elif c == 'n':
            notebooks_screen()
        elif c == 'i':
            print ""
            f = termdisplay.ask_input("Filename:")
            backend.import_from_base(f)
        elif c == 'q' or c == '\x03': # ctrl-c
            backend.cleanup()
        else:
            continue

if __name__ == "__main__":
    print "Please run init.py to start the Indexer."
