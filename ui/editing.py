# -*- coding: utf-8 -*-
from time import sleep
import db.database
import db.entries
import db.utilities
import termdisplay

def screen(entry):
    """
    Display options for editing or deleting an entry.

    Argument: the text of the entry to modify.
    """

    while True:
        termdisplay.print_title()
        termdisplay.fake_input("Edit entry:", entry)

        keys = ['C', 'D', 'Q']
        commands = {'F':'Fix Entry', 'C':'Coalesce entry', 'D':'Delete entry',
                    'S':'Save changes', 'U':'Undo changes', 'Q':'Quit'}
        termdisplay.print_commands(keys, commands, '')

        termdisplay.entry_square()
        c = termdisplay.getch().lower()
        if c == 'f':
            print ""
            # ask if we want to leave a moved ref
            new_entry = termdisplay.ask_input("Change to:")
            if db.entries.get_eid(new_entry):
                print "That entry already exists! Try a different one, or use coalesce."
                print "~ Press any key to continue ~",
                termdisplay.getch()
                continue
            else:
                db.entries.correct_entry(entry, new_entry)
                screen(new_entry)
            return
        elif c == 'c':
            print ""
            moveInto = termdisplay.ask_input("Coalesce into:")
            if not db.entries.get_eid(moveInto):
                print "That entry doesn't exist! Try again, or use fix."
                print "~ Press any key to continue ~",
                termdisplay.getch()
                continue
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
                return
                # consider trying to pull up the new entry

        elif c == 'd':
            eid = db.entries.get_eid(entry)
            ocrs = len( db.entries.fetch_occurrences(eid) )
            print "\nThere are %i occurrences associated with that entry." % ocrs
            print "They will be permanently lost.\n"
            doContinue = termdisplay.ask_input("Continue? (y/n)")
            if doContinue.lower() == 'y':
                db.entries.delete_entry(eid)
                print "Deleted."
                db.database.connection.commit()
                sleep(0.25)
                return
            else:
                continue
        #elif c == 's':
        #    db.database.connection.commit()
        #    print "\b\b\bSaved."
        #    sleep(0.5)
        #elif c == 'u':
        #    db.database.connection.rollback()
        #    print "\b\b\b\bUndone."
        #    sleep(0.5)
        #    screen(entry)
        #    return
        elif c == 'q':
            # presumably user wants to save changes
            db.database.connection.commit()
            return
        elif c == '\x03': # ctrl-c
            db.utilities.sigint_handler()
        else:
            print ""
            continue
