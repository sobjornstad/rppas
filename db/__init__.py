# -*- coding: utf-8 -*-
# Copyright (c) 2014 Soren Bjornstad <contact@sorenbjornstad.com>
# License: GNU AGPL, version 3 or later; see COPYING for details

# make sure we have a config file first; some of the other imports need it too
try:
    from config import PASSWORD
except:
    print "Whoops! You don't have a configuration file!"
    print "To correct this, rename the default 'config.py.DEFAULT' file"
    print "to 'config.py' and edit it as desired, then start the program again."
    import sys
    sys.exit(1)

import getpass
import signal
import ui.main
import database
import utilities

def access_control():
    """
    Ask for a password; should be run before initialize(). The DB is not
    encrypted and the password is stored in plaintext in config.py; this is
    just a fast way to keep out casual meddlers.

    If PASSWORD is set to nothing in config.py, automatically continue.

    Exits the program if the password is not correct; no return.
    """

    if not PASSWORD:
        return

    pw = getpass.getpass("Password: ")
    if pw != PASSWORD:
        exit()

access_control()
signal.signal(signal.SIGINT, utilities.sigint_handler)
database.initialize()
