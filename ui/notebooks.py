# -*- coding: utf-8 -*-

import termdisplay
from termdisplay import getch
import config
from time import sleep
import db.notebooks
import db.utilities

def add():
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
        nid = db.notebooks.get_nid(ntype, nnum)
        if nid != 0:
            print "Notebook already exists!"
        else:
            break

    while True:
        dopened = termdisplay.ask_input("Date opened:", extended=True)
        dclosed = termdisplay.ask_input("Date closed:", extended=True)
        if not (db.utilities.valid_date(dopened) and db.utilities.valid_date(dclosed)):
            print "Invalid date(s)!"
            print ""
        elif dopened > dclosed:
            print "Specified open date is after close date!"
            print ""
        else:
            break

    db.notebooks.create(ntype, nnum, dopened, dclosed)
    db.database.connection.commit()

def edit():
    """
    Edit the dates a notebook was open. Gets information within the function
    and returns nothing.
    """

    ntype = termdisplay.ask_input("Type to edit:")
    nnum = termdisplay.ask_input("Number to edit:", extended=True)

    nid = db.notebooks.get_nid(ntype, nnum)
    if nid == 0:
        print "Error -- no matches."
        termdisplay.entry_square()
        getch()
        return

    dopened, dclosed = db.notebooks.get_info(nid, "dopened, dclosed")
    while True:
        nopen = termdisplay.ask_input("Open date [%s]:" % dopened, extended=True)
        nclose = termdisplay.ask_input("Close date [%s]:" % dclosed, extended=True)

        # use current as defaults (bracketed)
        if not nopen:
            nopen = dopened
        if not nclose:
            nclose = dclosed

        # make sure dates are valid
        if not db.utilities.valid_date(nopen) and db.utilities.valid_date(nclose):
            print "Invalid date(s). Try again.\n"
        elif nopen > nclose:
            print "Specified open date is after close date! Try again.\n"
        else:
            break

    db.notebooks.rewrite_dates(nid, nopen, nclose)

def delete():
    while True:
        print ""
        ntype = termdisplay.ask_input("Type to delete:")
        if ntype not in config.NOTEBOOK_TYPES:
            print "Invalid notebook type!"
        else:
            break

    while True:
        nnum = termdisplay.ask_input("Number to delete:", extended=True)
        nid = db.notebooks.get_nid(ntype, nnum)
        try:
            nid = int(nid)
        except:
            print "Invalid number!"
            continue
        if nid == 0:
            print "Notebook does not exist!"
        else:
            break

    db.notebooks.delete(nid)

def screen():
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
            nlist = db.notebooks.dump_dated(dopened, dclosed)
        elif filtered == 'openAt':
            nlist = db.notebooks.dump_open(dat)
        else:
            nlist = db.notebooks.dump()

        if not nlist:
            print "(no results)"
        for i in nlist:
            print formatStr % ((i[0] + str(i[1])), i[2], i[3])

        keys = ['A', 'E', 'D', 'S', 'U', ' ', 'F', 'O', 'C', 'V', 'Q']
        commands = {'A':'Add', 'E':'Edit', 'D':'Delete',
                    'F':'Filter', 'O':'Open at time',
                    'C':'Clear filter', 'V':'Events',
                    'S':'Save changes', 'U':'Undo changes', 'Q':'Quit'}
        termdisplay.print_commands(keys, commands, '')
        termdisplay.entry_square()

        c = getch().lower()
        if c == 'a':
            add()
        elif c == 'e':
            print ""
            edit()
        elif c == 'd':
            delete()
        elif c == 'f':
            while True:
                print ""
                dopened = termdisplay.ask_input("Opened after:")
                dclosed = termdisplay.ask_input("Closed before:", extended=True)
                if db.utilities.valid_date(dopened) and db.utilities.valid_date(dclosed):
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
        elif c == 's':
            backend.connection.commit()
            print "\b\b\bSaved."
            sleep(0.5)
        elif c == 'u':
            backend.connection.rollback()
            print "\b\b\b\bUndone."
            sleep(0.5)
        elif c == 'q':
            return
        elif c == '\x03': # ctrl-c
            backend.sigint_handler()
