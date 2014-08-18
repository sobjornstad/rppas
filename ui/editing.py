# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

import readline
from time import sleep
import db.database
import db.entries
import db.utilities
import termdisplay

def screen(entry):
    """
    Display options for editing or deleting an entry.

    Argument: the text of the entry to modify. This argument is passed through
    to all other functions in this module, which modify "the current entry",
    thus this argument is a sort of state even though this isn't a class.
    """

    while True:
        termdisplay.print_title()
        termdisplay.fake_input("Edit entry:", entry)

        keys = ['F', 'C', 'D', 'Q']
        commands = {'F':'Fix entry', 'C':'Coalesce entry', 'D':'Delete entry',
                    'S':'Save changes', 'U':'Undo changes', 'Q':'Quit'}
        termdisplay.print_commands(keys, commands, '')

        termdisplay.entry_square()
        c = termdisplay.getch().lower()
        if c == 'f':
            didWork = fix_entry(entry)
            if didWork: return
            else: continue
        elif c == 'c':
            didWork = coalesce_entry(entry)
            if didWork: return
            else: continue
        elif c == 'd':
            delete_entry(entry)
            return
        elif c == 'q':
            # presumably user wants to save her changes
            db.database.connection.commit()
            return
        elif c == '\x03': # ctrl-c
            db.utilities.sigint_handler()
        else:
            print ""
            continue

def fix_entry(entry):
    """
    Allow user to change name of an entry. It is called 'fix' because the only
    plausible reason to do so in this context is to correct a typo or other
    error.

    Returns True if the fix was successful, False if user chose an invalid new
    name (i.e., one that already exists).
    """

    print ""
    # ask if we want to leave a moved ref
    new_entry = termdisplay.ask_input("Change to:")
    if db.entries.get_eid(new_entry):
        print "That entry already exists! Try a different one, or use coalesce."
        print "~ Press any key to continue ~",
        termdisplay.getch()
        return False
    else:
        db.entries.correct_entry(entry, new_entry)
        screen(new_entry)
        return True

def coalesce_entry(entry):
    """
    The companion to fix_entry(), allows user to move the occurrences from the
    current entry into another, thereby combining or 'coalescing' them.

    Returns True if the coalesce was successful, False if user chose an invalid
    'to' name (i.e., one that doesn't exist).
    """

    print ""
    moveInto = termdisplay.ask_input("Coalesce into:")
    if not db.entries.get_eid(moveInto):
        print "That entry doesn't exist! Try again, or use fix."
        print "~ Press any key to continue ~",
        termdisplay.getch()
        return False
    else:
        doRedir = termdisplay.ask_input("Leave redirect (y/n)?")
        if doRedir.lower() == 'n':
            db.entries.coalesce_entry(entry, moveInto, redir=False)
        else:
            # 'yes' goes in else to avoid deleting if neither y nor n
            db.entries.coalesce_entry(entry, moveInto, redir=True)
        print "Coalesced."
        db.database.connection.commit()
        sleep(0.25)
        screen(moveInto) # change view to entry coalesced into
        return True # fall through to search screen

def delete_entry(entry):
    """
    Dead simple, allows user to delete the current entry (and any associated
    occurrences).

    Returns True if the delete was successful, False if user canceled the
    delete.
    """

    eid = db.entries.get_eid(entry)
    ocrs = len( db.entries.fetch_occurrences(eid) )
    print "\nThere %s %i occurrence%s associated with that entry." % \
            ('is' if ocrs == 1 else 'are', ocrs, '' if ocrs == 1 else 's')
    print "%s will be permanently lost.\n" % ('It' if ocrs == 1 else 'They')
    doContinue = termdisplay.ask_input("Continue? (y/n)")
    if doContinue.lower() == 'y':
        db.entries.delete_entry(eid)
        print "Deleted."
        db.database.connection.commit()
        sleep(0.25)
        return True
    else:
        return False
