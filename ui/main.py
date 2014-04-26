# -*- coding: utf-8 -*-

import db.database
import db.importing
import adding
import notebooks
import searching
import termdisplay

def screen():
    """
    Screen to select other screens. If you're working on this and aren't
    familiar with the concept of a main menu, get out.
    """

    keys = ['S', 'P', 'A', 'N', 'I', 'X', 'Q']
    commands = {'S':'Search',
                'P':'Print Index',
                'A':'Add Entries',
                'N':'Notebooks',
                'I':'Import',
                'X':'Export',
                'Q':'Quit',
               }

    while True:
        termdisplay.print_title()
        termdisplay.print_commands(keys, commands, '  Main')
        termdisplay.entry_square()
        c = termdisplay.getch().lower()

        if c == 's':
            searching.search_screen()
        elif c == 'n':
            notebooks.screen()
        elif c == 'a':
            adding.screen()
        elif c == 'i':
            print ""
            f = termdisplay.ask_input("Filename:")
            db.importing.from_base(f)
        elif c == 'q' or c == '\x03': # ctrl-c
            db.database.cleanup()
        else:
            continue
