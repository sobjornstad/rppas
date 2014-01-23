import termdisplay
import backend
from termdisplay import getch

def print_title():
    termdisplay.clearscreen()
    print termdisplay.center(termdisplay.colors.WHITE + "  The Records Project Indexing Search Engine")
    print termdisplay.horizontalRule() + termdisplay.colors.ENDC
    print ""

def lookup_by_number(results):
    """
    Called after a search to ask for input and look up an item by number.
    """

    index = termdisplay.ask_input("Lookup:")
    try:
        index = int(index)
    except ValueError:
        # maybe they typed the word instead; if not, they'll be told no matches
        lookup_action(index)
    else:
        # lookup by word
        lookup_action(results[index][0])

def lookup_action(search):
    """
    Find the entry being looked up and print out its occurrences.
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
            charcount += len("%s%i.%s" % (i[1][0], i[1][1], i[1][2]))
            if charcount > termdisplay.SCREEN_WIDTH:
                print '\b,\n ' + ' ' * termlen,
                loopcount = 0
                charcount = termlen + 2 + 12

            formatStr = termdisplay.colors.ENDC + "%s" + \
                        termdisplay.colors.GREEN + "%i" + \
                        termdisplay.colors.BLUE + ".%s" + \
                        termdisplay.colors.ENDC
            if loopcount == 0:
                print formatStr % (i[1][0], i[1][1], i[1][2]),
            else:
                print "\b, " + formatStr % (i[1][0], i[1][1], i[1][2]),

            charcount += 2 # for the comma and space
            loopcount += 1
    else:
        # should only happen when manual lookup by entering name
        print "No results."

    print ""
    termdisplay.entry_square()

def search_screen():
    print_title()
    search = termdisplay.ask_input("Search:")
    results, matches = backend.search_entries(search)
    if matches:
        for i in matches:
            print "%i:\t%s" % (i, matches[i][0])
    else:
        print "No results."

    keys = ['L', 'S', 'Q']
    commands = {'L':'Lookup', 'S': 'Search again', 'Q':'Quit'}
    print_commands(keys, commands, '')
    termdisplay.entry_square()

    while True:
        c = getch()
        if c == 'l':
            print ""
            lookup_by_number(matches)
        elif c == 's':
            r = search_screen()
            if r == 'break':
                return 'break' # see below comment on 'q'
        elif c == 'q':
            # even if we run search several times, we only want to press q once
            return 'break'
        elif c in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # simply look up that item; last line of the lookup_by_number fn
            print ""
            lookup_action(matches[int(c)][0])
        else:
            print '\b!\b',
            continue

def print_commands(keys, commands, title):
    print termdisplay.center(termdisplay.colors.GREEN + title + termdisplay.colors.ENDC)
    displayString = ''
    for i in keys:
        displayString += termdisplay.colors.BLUE + '<' + i + '> ' + \
              termdisplay.colors.ENDC + commands[i] + '\n'

    print termdisplay.text_box(displayString.rstrip())

def main_screen():
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
        print_title()
        print_commands(keys, commands, '  Main')
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
