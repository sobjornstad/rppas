# -*- coding: utf-8 -*-

import database
import entries

def lookup(search):
    """
    Look up the occurrences of an entry given the name of the entry.

    Returns same format as fetch_occurrences(): a list of tuples
    (ntype, nnum, page). Return None if there are no matches.
    """

    eid = events.get_eid(search)
    if not eid:
        return

    matches = entries.fetch_occurrences(eid)
    return matches

def events(search):
    """
    Given a search string, find events containing that substring. Quite similar
    to search_entries.

    Returns a dictionary:
    - KEYS: numerical IDs (to be displayed and used to select)
    - VALUES: events (as strings)
    """

    search = "%" + search + "%"
    database.cursor.execute('SELECT event FROM events \
                    WHERE event LIKE ? \
                    ORDER BY nid, event', (search,))

    matches = {}
    matchnum = 1
    for match in database.cursor.fetchall():
        matches[matchnum] = match[0]
        matchnum += 1

    if not matches:
        return 0, None
    else:
        return len(matches), matches

def entries(search, substrfilters=[]):
    """
    Given a search string, find entries containing that substring.

    Returns a tuple of the number of matches, as well as a dictionary:
        - KEYS: numerical IDs (to be displayed and used to select)
        - VALUES: entries (as strings)

    To look up occurrences for one of the entries, then, the user can enter a
    number and the program can pull out the text of the entry using the
    dictionary, then use get_entry_eid to find EIDs and look up occurrences by
    that.

    Optional argument: a list of additional substring filters or "subsearches"
    to search within the search.
    """

    search = "%" + search + "%"
    query = 'SELECT name FROM entries ' \
            'WHERE name LIKE ? '
    if substrfilters:
        for i in range(len(substrfilters)):
            query += "AND name LIKE ? "
            if not (substrfilters[i][0] == '%' and substrfilters[i][0] == '%'):
                substrfilters[i] = "%" + substrfilters[i] + "%"

    query += 'ORDER BY name'
    params = [search] + substrfilters
    database.cursor.execute(query, params)

    matches = {}
    matchnum = 1
    for match in database.cursor.fetchall():
        matches[matchnum] = match[0]
        matchnum += 1

    if not matches:
        return 0, None
    else:
        return len(matches), matches
