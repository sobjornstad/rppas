# -*- coding: utf-8 -*-

from config import PASSWORD, VALID_YEAR_RANGE, NOTEBOOK_TYPES, NOTEBOOK_SIZES
import ui.termdisplay
import database
import notebooks

def valid_date(date, unlimited_years=False):
    """
    Determine if a given date (YYYY-MM-DD string) is valid. Returns True if
    yes, False if problem. Will safely catch non-integer days.

    By default, will check to make sure the year could reasonably be within my
    lifetime or nearby (1990-2100). If this is not desired, pass
    unlimited_years = True.
    """

    month_days = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30,
                  7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

    # catch YYYY-MM-DD deviations
    date = date.split('-')
    try:
        year = date[0]
        month = date[1]
        day = date[2]
    except IndexError:
        return False
    if len(date) != 3: return False
    if len(year) != 4: return False
    if len(month) != 2: return False
    if len(day) != 2: return False

    # catch non-int-convertible values
    try:
        year, month, day = int(year), int(month), int(day)
    except ValueError:
        return False

    # catch out-of-bounds month and days
    if not 1 <= month <= 12: return False
    if not 1 <= day <= month_days[month]: return False

    # catch 2/29's on non-leap years
    if (month == 2) and (day == 29) and (year % 4): return False
    if (month == 2) and (day == 29) and (not year % 4):
        if (not year % 100) and (year % 400): return False

    # catch years obviously out of user's lifetime (configurable)
    # default 1990-2100
    if not unlimited_years:
        if not VALID_YEAR_RANGE[0] <= year <= VALID_YEAR_RANGE[1]:
            return False

    # if all these checks pass, the date should be valid
    return True

def validate_location(ntype, nnum, pagenum=None):
    """
    Check whether information the user has entered for a Nearby or When Was
    query can actually be used successfully to look up information.

    Requires ntype and nnum; pagenum is optional.

    Returns True if valid, False if invalid.
    """

    # make sure notebook exists
    if ntype not in NOTEBOOK_TYPES:
        return False
    if type(nnum) != int:
        return False
    if not notebooks.get_nid(ntype, nnum):
        return False

    # check that page is positive and less than max for that notebook
    if pagenum: # optional test
        if type(pagenum) != int:
            return False
        if (pagenum < 1) or (pagenum > NOTEBOOK_SIZES[ntype]):
            return False

    return True

def zero_pad(i, ntype):
    """
    Add appropriate leading zeroes for an occurrence string. Determines whether
    one is needed based on the string length and the notebook type under
    consideration.

    Arguments: string to pad, notebook type.
    Return: padded string.
    """

    if len(i) == 2:
        if NOTEBOOK_SIZES[ntype] <= 99:
            pass
        elif NOTEBOOK_SIZES[ntype] <= 999:
            i = '0' + i
    elif len(i) == 1:
        assert ntype in NOTEBOOK_TYPES, "invalid ntype %r, valids %r" % \
                (ntype, NOTEBOOK_TYPES)
        if NOTEBOOK_SIZES[ntype] <= 99:
            i = '0' + i
        elif NOTEBOOK_SIZES[ntype] <= 999:
            i = '00' + i
        else:
            termdisplay.warn("Your notebooks are very large. Unable to correctly pad page numbers with leading zeroes.")

    return i

def unzero_pad(s):
    """
    Remove any leading zeroes from the argument string and return modified
    string. Dead simple.
    """

    return s.lstrip('0')

def sigint_handler(signal='', frame=''):
    """
    Run when Control-C is pressed at a menu or prompt. Runs the cleanup()
    routine to commit any stray transactions and exit nicely.

    Two optional arguments to accommodate signal.signal() as well as manual
    calling. No return.
    """

    print ""
    #print "Caught SIGINT, cleaning up..."
    database.cleanup()
