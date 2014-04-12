# -*- coding: utf-8 -*-

import database
import entries
import notebooks
import utilities

def from_base(filename):
    """
    Import from my previous database format, a Base file (exported to TSV).

    Argument: name of the file to import. No return.
    """

    f = open(filename)
    for line in f:
        EID, ntype, nnum, page, entry = line.split('\t')
        nnum = int(nnum)
        entry = entry.strip()
        page = page.strip()

        notebooks.create(ntype, nnum, "NULL", "NULL") # cancels if existing

        # Commas signify several occurrences of the entry, to be processed
        # separately, but a 'see FOO' entry might have commas and shouldn't
        # be split. This might break on a "see also," but we can't be perfect.
        if ',' in page and 'see' not in page:
            pages = page.split(',')
            for i in pages:
                i = i.strip()
                i = utilities.zero_pad(i, ntype)
                entries.add_occurrence(entry, ntype, nnum, i)
        else: # single entry
            page = utilities.zero_pad(page, ntype)
            entries.add_occurrence(entry, ntype, nnum, page)

    database.connection.commit()
