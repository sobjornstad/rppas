# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import textwrap
from time import sleep
import config
import db.events
import db.notebooks
import db.database
import termdisplay

def add(nid):
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

    ok = db.events.create(nid, event, isSpecial)
    if ok is None:
        print "Whoops, that event already exists!"
        termdisplay.entry_square()
        termdisplay.getch()

def delete(bothlist):
    """
    Ask for the key number to delete and remove it from the database.

    Argument: The bothlist list containing the current state of events (no
              pun intended) and specials.
    Return: None.
    """

    while True:
        todel = termdisplay.ask_input("Number to delete:")
        try:
            todel = int(todel)
        except ValueError:
            print "Enter the number of the item to delete."
        else:
            break

    bothlist[todel - 1].delete() # - 1 because counter starts at 1

    # we don't need to delete from the list itself because it's rebuilt on
    # returning to the events list

def screen(ntype=None, nnum=None):
    """
    Screen that allows the user to look at and modify events in a selected
    notebook.

    Optional arguments specify the notebook type and number to show; if not
    specified, the user will be asked which one to look at.
    """

    first = True # clear screen only when switching books; 
                 # keep the table of books displayed the first time
    needsUserInput = True if (ntype == None and nnum == None) else False

    if not needsUserInput and ntype != 'CB':
        # events are only a thing for CBs
        termdisplay.warn("Tried to open events for a non-CB notebook!")
        return False

    while True:
        if first:
            first = False
            print ""
        else:
            termdisplay.print_title()

        if needsUserInput:
            ntype = 'CB'
            nnum = termdisplay.ask_input("CB number to view:", extended=True)

        nid = db.notebooks.get_nid(ntype, nnum)
        if nid == 0:
            first = True # don't refresh screen
            print "Nonexistent notebook, please try again."
        else:
            break

    while True:
        termdisplay.print_title()
        dopened, dclosed = db.notebooks.get_info(nid, "dopened, dclosed")
        events, specials = db.events.fetch_in_notebook(nid)
        bothlist = events + specials # for later reference

        # output screen header
        print termdisplay.center("Events for %s%s%s%s" % (
            termdisplay.colors.GREEN, ntype, nnum, termdisplay.colors.ENDC))
        print termdisplay.center("  %s%s%s – %s%s%s" % (
            termdisplay.colors.WHITE, dopened, termdisplay.colors.RED,
            termdisplay.colors.WHITE, dclosed, termdisplay.colors.ENDC))

        # output events list
        counter = 1
        print termdisplay.colors.BLUE + "\nEvents:" + termdisplay.colors.ENDC
        for i in events:
            lines = textwrap.wrap(i.getText(), config.SCREEN_WIDTH - 8)
            print "%i:\t%s" % (counter, lines.pop(0))
            for line in lines:
                print "   \t%s" % line
            counter += 1

        # counter continues for specials
        print termdisplay.colors.BLUE + "\nSpecials:" + termdisplay.colors.ENDC
        for i in specials:
            lines = textwrap.wrap(i.getText(), config.SCREEN_WIDTH - 8)
            print "%i:\t%s" % (counter, lines.pop(0))
            for line in lines:
                print "   \t%s" % line
            counter += 1

        keys = ['A', 'D', 'R', 'S', 'U', 'B', '+', '-', 'Q']
        commands = {'A':'Add', 'D':'Delete', 'R':'Reposition',
                    'S':'Save changes', 'U':'Undo changes', 'B':'Change book',
                    '+':'Next book', '-':'Previous book', 'Q':'Quit'}
        termdisplay.print_commands(keys, commands, '')

        termdisplay.entry_square()
        c = termdisplay.getch().lower()
        if c == 'a':
            print ""
            add(nid)
        elif c == 'd':
            print ""
            delete(bothlist)
        elif c == 'r':
            reposition(bothlist, nid)
        elif c == 's':
            db.database.connection.commit()
            print "\b\b\bSaved."
            sleep(0.5)
        elif c == 'u':
            db.database.connection.rollback()
            print "\b\b\b\bUndone."
            sleep(0.5)
        elif c == 'b':
            r = screen()
            return
        elif c in ('+', '-'):
            adjNid = db.notebooks.adjacent(nid, (1 if c == '+' else -1))
            ntype, nnum = db.notebooks.get_info(adjNid, "ntype, nnum")
            r = screen(ntype, nnum)
            return
        elif c == 'q':
            # even if we run search several times, we only want to press q once
            return
        elif c == '\x03': # ctrl-c
            utilities.sigint_handler()
        else:
            print ""
            continue

def reposition(bothlist, nid):
    ev1, ev2 = None, None
    while True:
        print ""
        while True:
            ev1 = termdisplay.ask_input("Event to reposition:")
            try:
                ev1 = int(ev1)
            except ValueError:
                print "Use event numbers to select events to reposition."
                print ""
                continue
            else:
                try:
                    if (ev1 - 1) < 0:
                        # would select from end of list
                        raise IndexError
                    Event1 = bothlist[ev1 - 1]
                except IndexError:
                    print "Invalid event number.\n"
                    continue
                isSpec1 = Event1.isSpecial()
                break

        while True:
            ev2 = termdisplay.ask_input("Swap with:", True)
            try:
                ev2 = int(ev2)
            except ValueError:
                print "Use event numbers to select events to reposition."
                print ""
                continue
            else:
                try:
                    if (ev2 - 1) < 0:
                        raise IndexError
                    Event2 = bothlist[ev2 - 1]
                except IndexError:
                    print "Invalid event number.\n"
                    continue
                isSpec2 = Event2.isSpecial()
                break

        if isSpec1 is None or isSpec2 is None:
            termdisplay.warn("Something went wrong -- one of those "
                             "events doesn't exist.")
        elif (isSpec1 and not isSpec2) or (isSpec2 and not isSpec1):
            print "You cannot swap a special and non-special event."
        else:
            db.events.reorder(Event1, Event2, nid)
            break
