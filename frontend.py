import termdisplay
import backend
from termdisplay import getch

def print_title():
    termdisplay.clearscreen()
    print termdisplay.center(termdisplay.colors.WHITE + "  The Records Project Indexing Search Engine")
    print termdisplay.horizontalRule() + termdisplay.colors.ENDC
    print ""

def print_main_commands():
    keys = ['S', 'L', 'P', 'E', 'N', 'I', 'X', 'Q']
    commands = {'S':('Search', ' ' * 5),
                'P':('Print Index', '  '),
                'L':('Lookup', ' '),
                'Q':('Quit', '\n'),
                'N':('Notebooks', '  '),
                'E':('Edit Entries', ' '),
                'X':('Export', ' '),
                'I':('Import', '')
               }

    print termdisplay.center(termdisplay.colors.GREEN + '  Main' + termdisplay.colors.ENDC)
    displayString = ''
    for i in keys:
        displayString += termdisplay.colors.BLUE + '<' + i + '> ' + \
              termdisplay.colors.ENDC + commands[i][0] + '\n'

    print termdisplay.text_box(displayString.rstrip())

def main_screen():
    while True:
        print_title()
        print_main_commands()
        termdisplay.entry_square()
        c = getch()

        if c == 's':
            search_screen()
        elif c == 'q' or c == '\x03': # ctrl-c
            exit()
        else:
            continue

if __name__ == "__main__":
    main_screen()
