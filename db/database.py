# -*- coding: utf-8 -*-

import config
import sqlite3 as sqlite
import sys

### FULL-DATABASE OPERATIONS ###

def initialize():
    """
    Connect to the database; initialize backend module variables connection
    and cursor. Should be run when importing this module; no reason to do so
    thereafter.
    """

    global connection, cursor
    connection = sqlite.connect(config.DATABASE_FILENAME)
    connection.text_factory = str # fix for some weird Unicode error
    cursor = connection.cursor()
    print "database initialized"

def cleanup():
    """Commit any remaining changes and quit program. Obviously no return."""
    connection.commit()
    connection.close()
    sys.exit(0)
