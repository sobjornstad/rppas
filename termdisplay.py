# -*- coding: utf-8 -*-

import os
from pyparsing import *
from config import SCREEN_WIDTH, TITLE

### CONSTANTS AND CLASSES ###

class colors:
    """
    A class storing ANSI escape codes for coloring text. All data are strings.
    To use, do something like 'print colors.RED + "red text" + colors.ENDC'.

    Original source (this version somewhat modified):
    http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    """

    BLACK = '\033[40m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    ENDC = '\033[0m'

class moveCodes:
    """
    A class storing ANSI escape codes for moving the cursor.
    """

    UP1 = "\033[1A"

class lines:
    """
    A class storing Unicode line-drawing characters. All data are single-char
    strings.
    """

    ACROSS='═'
    DOWN  ='║'
    ULCORN='╔'
    URCORN='╗'
    BLCORN='╚'
    BRCORN='╝'

class _Getch:
    """
    Code for retrieving a single character from the screen. Does not echo it.
    Source: http://code.activestate.com/recipes/134892/
    """

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    """Companion code for _Getch used on Unix. Same source."""

    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    """Companion code for _Getch used on Windows. Same source."""

    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

# create getch object (to be imported by other modules)
getch = _Getch()


### STRING MODIFIERS ###
# These don't print anything, but just return a styled/modified string.

def stripAnsi(string):
    """
    Return a string stripped of any ANSI control characters. This is useful if
    you need to measure the length of the string for centering and whatnot.

    Requires all imported from the pyparsing library (from pyparsing import *).

    Source:
    http://stackoverflow.com/questions/2186919/
    getting-correct-string-length-in-python-for-strings-with-ansi-color-codes
    """

    ESC = Literal('\x1b')
    integer = Word(nums)
    escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer,';')) +
                    oneOf(list(alphas)))

    nonAnsiString = lambda s : Suppress(escapeSeq).transformString(s)
    unColorString = nonAnsiString(string)
    return unColorString

def calculatePadding(textLength, fullRequested=False, alignLeft=None):
    """
    Given some length of a string and possibly other parameters, returns a
    string consisting of spaces to be used for aligning on terminal output.

    For centering:
        Pass only the textLength parameter. The string returned will be
        SCREEN_WIDTH minus the length of the argument divided by 2, which can
        be placed before the string to center it on the screen.
    For creating a second column:
        Pass textLength and the alignLeft parameter with the column of the
        console you want to align the second column's beginning to. Normally
        this will be COLUMN_2_COLUMN.
    Examples:
        padding = calculatePadding(len(stringToDisplay))
        padding = calculatePadding(len(column1String), alignLeft=50)

    Note: The fullRequested parameter, which avoids dividing the padding by 2
    as described under "For centering" is currently not used for anything. It
    is implied to be True and automatically reset from its default of False
    when alignLeft is given a value.

    This function is copied verbatim from my mental math problems program, and
    some of the options are probably not necessary (right now!).
    """

    if alignLeft is not None:
        fullRequested = True
        assert(alignLeft < SCREEN_WIDTH), \
            "cannot align to column beyond screen width"

    assert(type(textLength) is int), \
        "calculatePadding takes an integer length, not a string"

    if alignLeft:
        padding = (alignLeft - textLength)
    else:
        # normal alignment request
        padding = (SCREEN_WIDTH - textLength)

    if not fullRequested:
        padding /= 2

    assert(padding > 0), "Not enough space to pad! textLength = %r, " \
                         "padding = %r, SCREEN_WIDTH = %r, alignLeft = %r" % \
                         (textLength, padding, SCREEN_WIDTH, alignLeft)

    padding = ' ' * padding
    return padding

def center(string):
    """
    Given a string, return that string with padding added to center it on a
    screen of the size given in config's SCREEN_WIDTH.
    """

    return calculatePadding(len(stripAnsi(string))) + string

def horizontalRule(char='—'):
    """
    Return a string that is a full-screen horizontal rule for the current
    screen width.  Optional argument: the character to use for the rule.
    """

    return char * SCREEN_WIDTH

def text_box(text, centerBox=True, centerText=False):
    """
    Return the string for a box containing the provided string.

    Arguments:
    - text: The text. Can be multiple lines; each line should not be longer than
      (SCREEN_WIDTH - 4) or an error will be thrown.
    - centerBox: Whether to center the box within the SCREEN_WIDTH. Default true.
    - centerText: Whether to center the text within the box. Default false.
    """

    if '\n' in text:
        text = text.split('\n')
    else:
        text = [text]

    # find the lengths of each string so we know how much padding to use later
    textMeasure = []
    for i in range(len(text)):
        textMeasure.append(stripAnsi(text[i]))

    # Find longest line to know how wide to make the box; make sure the box
    # isn't wider than the screen.
    # Account for 4 extra columns: 2 for padding between box/text, 2 for box
    width = len(max(textMeasure, key=len)) + 2
    assert ((width + 2) <= SCREEN_WIDTH), "Line %s too long!" % max(text, key=len)

    if centerBox:
        boxPadding = calculatePadding(width)
    else:
        boxPadding = ''

    boxString = ''
    boxString += boxPadding + lines.ULCORN + (lines.ACROSS * width) + lines.URCORN + '\n'
    for i in range(len(text)):
        if centerText:
            # calculate padding; center one to the left if perfect center in box not possible
            pad = width - len(textMeasure[i])
            leftpad = ' ' * (pad / 2)
            if (pad % 2):
                rightpad = ' ' * (pad / 2 + 1)
            else:
                rightpad = ' ' * (pad / 2)
        else:
            leftpad = ' '
            rightpad = ' ' * (width - len(textMeasure[i]) - 1)

        boxString += boxPadding + lines.DOWN + leftpad + text[i] + rightpad + lines.DOWN + '\n'
    boxString += boxPadding + lines.BLCORN + (lines.ACROSS * width) + lines.BRCORN + '\n'

    return boxString


### PRINTERS ###
# These directly modify the screen.

def clearscreen():
    """Clear the console screen."""

    print "" # sometimes the display ends up off by a line if you don't do this
    if os.name == "posix":
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        os.system('CLS')
    else:
        print '\n' * 100

def entry_square():
    """
    Directly print a bracket-box to hold the cursor when waiting for
    single-char user input. Running this function draws the box and puts the
    cursor inside. No return.
    """

    padding = ' ' * (SCREEN_WIDTH - 3)
    print padding + colors.GREEN + "[ ]" + colors.ENDC + "\b\b",

def ask_input(prompt, extended=True):
    """
    Ask for a line of input with raw_input. Prints prompt (using appropriate
    color), returns the user's input.

    The optional extended parameter is used if there are several ask_inputs in
    a row, in which case there is too large a gap between them normally due to
    the carriage return when the user presses Enter. Extended should be
    enabled on ones subsequent to the first to remove this gap.
    """

    if extended:
        prompt = moveCodes.UP1 + prompt

    print colors.RED + prompt + colors.YELLOW,
    search = raw_input()
    print colors.ENDC
    return search

def print_title():
    """
    Clear the screen and print config.TITLE and an HR to the top of the screen.
    """

    clearscreen()
    print center(colors.WHITE + TITLE)
    print horizontalRule() + colors.ENDC
    print ""

def print_commands(keys, commands, title):
    """
    Display a menu of available commands. Arguments:
    - keys: a list of access keys, in the order they should appear in the menu
    - commands: a dictionary: keys the same as the list of keys above, values
      the text of the menu items
    - title: The text to display above the box. An empty string is fine.

    No return; the caller must get input and handle it.
    """

    print center(colors.GREEN + title + colors.ENDC)
    displayString = ''
    for i in keys:
        displayString += colors.BLUE + '<' + i + '> ' + \
              colors.ENDC + commands[i] + '\n'

    print text_box(displayString.rstrip())

def warn(message):
    """
    Halt to inform the user of a problem with the program or database. The
    message provided will be written after "WARNING: ".
    """

    print "WARNING: " + message
    raw_input("~ Strike any key to continue... ~")
