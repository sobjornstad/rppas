# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import db.search
import db.entries
import db.events
import db.notebooks
import db.utilities
import events
import editing
import termdisplay

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
        if (not results):
            print "Invalid lookup number."
            return
        elif ( (index > len(results)) or (index < 1) ):
            print "Invalid lookup number."
            return
        else:
            lookup_action(results[index])

def lookup_action(search):
    """
    Find the entry being looked up (by lookup_by_number) and print out its
    occurrences.
    """

    matches = db.search.lookup(search)

    if matches:
        print termdisplay.moveCodes.UP1 + termdisplay.colors.WHITE + \
                search + ":" + termdisplay.colors.ENDC,

        termlen = len(search) # to know how far to skip when breaking a line
        loopcount = 0
        # 2 is for chars already there (space); 5 is a buffer I don't understand (probably spaces between listed occurrences).
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
                print formatStr % (i[0], i[1], db.utilities.unzero_pad(i[2])),
            else:
                print "\b, " + formatStr % (i[0], i[1], db.utilities.unzero_pad(i[2])),

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
        if db.utilities.validate_location(ntype, nnum, page):
            break
        else:
            print "Invalid entry!"

    results = db.entries.occurrences_around(ntype, nnum, int(page))

    formatStr = termdisplay.colors.GREEN + "%s%i" + \
                termdisplay.colors.ENDC + '.' + \
                termdisplay.colors.BLUE + "%s\t" + \
                termdisplay.colors.WHITE + "%s" + \
                termdisplay.colors.ENDC

    #TODO: Ranges can cause tabbing to look ugly
    if results:
        for i in results:
            print formatStr % (ntype, int(nnum), db.utilities.unzero_pad(i[0]), i[1])
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
        if db.utilities.validate_location(ntype, nnum):
            break
        else:
            print "Invalid entry!"

    nid = db.notebooks.get_nid(ntype, nnum)
    events.screen(ntype, nnum)

def lookup_event(matches, key=None):
    if not key:
        key = termdisplay.ask_input("Number to look up:")
        try: key = int(key)
        except ValueError:
            print "Invalid lookup value!"
            lookup_event(matches)
            return

    try: evid = db.events.get_evid(matches[key])
    except IndexError:
        print "Invalid lookup value!"
        lookup_event(matches)
    else:
        nid = db.events.which_notebook(evid)
        ntype, nnum = db.notebooks.get_info(nid, "ntype, nnum")
        events.screen(ntype, nnum)

def search_events_screen(search=None):
    """
    Mostly the same code as search_screen, but searches events rather than
    index entries. Optional argument for search to run.
    """

    termdisplay.print_title()
    if not search:
        search = termdisplay.ask_input("Event search:")
    else:
        termdisplay.fake_input("Event search:", search)
    results, matches = db.search.events(search)
    if matches:
        for i in matches:
            print "%i:\t%s" % (i, matches[i])
    else:
        print "No results."

    keys = ['L', 'S', 'Q']
    commands = {'L':'Lookup', 'S':'Search again', 'Q':'Quit'}
    termdisplay.print_commands(keys, commands, '')

    while True:
        termdisplay.entry_square()
        c = termdisplay.getch().lower()
        if c == 'l':
            print ""
            lookup_event(matches)
            search_events_screen(search)
            return
        elif c == 's':
            search_events_screen()
            return
        elif c == 'q':
            return
        elif c == '\x03': # ctrl-c
            db.utilities.sigint_handler()
        elif c in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # simply look up that item
            print ""
            try:
                c = int(c)
            except:
                print "Invalid lookup number."
            if c > len(matches):
                print "Invalid lookup number."
            else:
                lookup_event(matches, c)
                search_events_screen(search)
                return
        else:
            print ""
            continue

def search_screen(search=None, substrfilters=[]):
    """
    Screen that allows the user to search for index entries matching a query,
    then optionally run a lookup, When was, or Nearby.

    Optional argument: the search to run. Otherwise the user will be asked.
    Second optional argument: one or more substrings to also require in the
    entries, to be used as a sort of search-within-a-search ("filter").
    """

    termdisplay.print_title()
    if not search:
        search = termdisplay.ask_input("Search:")
    else:
        termdisplay.fake_input("Search:", search)
        # display list of current filters below
        filtersString = ''
        for i in substrfilters:
            filtersString += i
            filtersString += ', '
        filtersString = filtersString[:-2]
        if filtersString:
            termdisplay.fake_input("Filter:", filtersString)

    results, matches = db.search.Entries(search, substrfilters)
    if matches:
        for i in matches:
            print "%i:\t%s" % (i, matches[i])
    else:
        print "No results."

    keys = ['L', 'S', 'F', 'U', 'N', 'W', 'V', 'E', 'R', 'Q']
    commands = {'L':'Lookup', 'S':'Search again', 'F':'Filter', 'U':'Unfilter',
                'N':'Nearby', 'W':'When was', 'V': 'Search events',
                'E':'Edit entry', 'R':'Reload', 'Q':'Quit'}
    termdisplay.print_commands(keys, commands, '')

    while True:
        termdisplay.entry_square()
        c = termdisplay.getch().lower()
        if c == 'l':
            print ""
            lookup_by_number(matches)
        elif c == 's':
            search_screen(substrfilters=[])
            return
        elif c == 'f':
            print ""
            newFilter = termdisplay.ask_input("Filter:")
            substrfilters.append(newFilter)
            search_screen(search, substrfilters)
            return
        elif c == 'u':
            search_screen(search, [])
            return
        elif c == 'w':
            when_was()
            search_screen(search, substrfilters)
            return
        elif c == 'n':
            nearby()
        elif c == 'v':
            search_events_screen(search)
            search_screen(search, substrfilters)
            return
        elif c == 'e':
            print ""
            entryNum = termdisplay.ask_input("Entry to edit:")
            try: editing.screen(matches[int(entryNum)])
            except ValueError:
                print "Invalid lookup number."
                continue
            search_screen(search, substrfilters)
            return
        elif c == 'r':
            search_screen(search, substrfilters)
            return
        elif c == 'q':
            # even if we run search several times, we only want to press q once
            return
        elif c == '\x03': # ctrl-c
            db.utilities.sigint_handler()
        elif c in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # simply look up that item; equivalent to the last lines of the
            # lookup_by_number() function
            print ""
            try:
                c = int(c)
            except:
                print "Invalid lookup number."

            if (not matches):
                print "Invalid lookup number."
            elif ( c > len(matches) ) or ( c < 1 ):
                print "Invalid lookup number."
            else:
                lookup_action(matches[c])
        else:
            print ""
            continue
