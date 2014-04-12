# -*- coding: utf-8 -*-

import getpass
import signal
from config import PASSWORD
import database
import ui.main
import utilities

def access_control():
    """
    Ask for a password; should be run before initialize(). The DB is not
    encrypted and the password is stored in plaintext in config.py; this is
    just a fast way to keep out casual meddlers.

    While working on the program, you probably want to comment the call out at
    the bottom of this file.

    Exits the program if the password is not correct; no return.
    """

    pw = getpass.getpass("Password: ")
    if pw != PASSWORD:
        exit()

#access_control() # comment this out while testing to avoid needing PW
signal.signal(signal.SIGINT, utilities.sigint_handler)
database.initialize()
