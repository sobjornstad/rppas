# -*- coding: utf-8 -*-

import getpass
import signal
from config import PASSWORD
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
