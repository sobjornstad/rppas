import backend

def import_from_base(filename):
    f = open(filename)
    for line in f:
        EID, ntype, nnum, page, entry = line.split('\t')
        nnum = int(nnum)
        entry = entry.strip()
        page = page.strip()

        backend.create_notebook(ntype, nnum, "NULL", "NULL", "NULL")

        # Commas signify several occurrences of the entry, to be processed
        # separately, but a 'see FOO' entry might have commas and shouldn't
        # be split.
        if ',' in page and 'see' not in page:
            pages = page.split(',')
            for i in pages:
                i = i.strip()
                backend.add_entry(entry, ntype, nnum, i)
        else: # single entry
            backend.add_entry(entry, ntype, nnum, page)

    backend.run_commit()
