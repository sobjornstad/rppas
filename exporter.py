import backend

def export_index(filename):
    writeString = ""
    for entry in backend.dump_index():
        eid, name = entry
        matches = backend.fetch_occurrences(eid)

        writeString += "%s\t" % name
        comma = False
        for i in matches:
            # don't put a comma before the first entry, but each time thereafter
            if comma:
                writeString += ","
            else:
                comma = True
            writeString += "%s%i.%s" % (i[1][0], i[1][1], i[1][2])
        writeString += "\n"

    f = open(filename, 'w')
    f.write(writeString)
    f.close()
