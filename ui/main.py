# -*- coding: utf-8 -*-

import termdisplay
from termdisplay import getch
import searching
import notebooks
import db.importing
import db.database

def screen():
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
            searching.search_screen()
        elif c == 'n':
            notebooks.screen()
        elif c == 'i':
            print ""
            f = termdisplay.ask_input("Filename:")
            db.importing.from_base(f)
        elif c == 'q' or c == '\x03': # ctrl-c
            db.database.cleanup()
        else:
            continue
