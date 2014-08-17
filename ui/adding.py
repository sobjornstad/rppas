# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import readline
import sys

import db.adding
import config
import termdisplay

def screen():
    """
    Screen for adding entries to the list. We save every time the list reaches
    5 elements, when we quit, or on user request.
    """

    nid = getNotebook()
    if not nid:
        return
    else:
        queue = db.adding.AdditionQueue(nid)

    print "Enter /help for information about adding commands."
    while True:
        entry = raw_input(termdisplay.colors.RED+"Entry: "+
                          termdisplay.colors.YELLOW)
        print termdisplay.colors.ENDC

        if entry == "/help":
            print "Available commands:"
            print "/help       - show this help screen"
            print "/history    - show list of added entries"
            print "/save       - save entries now"
            print "/strike [#] - remove previous entry(ies)"
            print "/queue      - show unsaved entries"
            print "/quit       - stop adding entries"
        elif entry == "/save":
            queue.dump()
        elif entry == "/queue":
            queue.showQueue()
        elif entry == "/history":
            queue.showHistory()
        elif entry.startswith("/strike"):
            if entry == "/strike": # no params
                queue.strike()
            else:
                parts = entry.split(' ')
                if len(parts) > 1:
                    try:
                        parts[1] = int(parts[1])
                    except ValueError: # not an int; ignore parameter
                        queue.strike()
                    else:
                        queue.strike(parts[1])
                else: # no parameter given
                    queue.strike()

        elif entry == "/quit":
            queue.dump()
            break
        else:
            page = termdisplay.ask_input("Page:", extended=True)
            queue.add(entry, page)


def getNotebook():
    """
    Ask user what notebook they want to add entries to and return the nid.
    Return None if the user entered a nonexistent (but valid) notebook.
    """

    print "\nWhat notebook do you want to add entries to?"
    while True:
        print ""
        ntype = termdisplay.ask_input("Type:")
        nnum = termdisplay.ask_input("Number:", extended=True)
        if ntype.upper() not in config.NOTEBOOK_TYPES:
            print "Invalid notebook type!"
            continue
        try: nnum = int(nnum)
        except:
            print "Invalid notebook number!"
            continue

        nid = db.notebooks.get_nid(ntype, nnum)
        if not nid:
            print "That notebook does not exist! Please create it first."
            raw_input("~ Strike any key to continue... ~")
            # allow creating it?
            return None
        return nid
