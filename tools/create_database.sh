#!/usr/bin/python
import sqlite3 as sqlite

# MAIN #
print "Records Project Paper Augmentation System Database Initializer"
DATABASE = raw_input("Type the name of the new DB to init: ")

connection = sqlite.connect(DATABASE)
cursor = connection.cursor()
cursor.execute('CREATE TABLE occurrences (oid INTEGER PRIMARY KEY, page TEXT, nid INTEGER, eid INTEGER)') #page must be text to support 'see's and such
cursor.execute('CREATE TABLE entries (eid INTEGER PRIMARY KEY, name TEXT)')
cursor.execute('CREATE TABLE notebooks (nid INTEGER PRIMARY KEY, ntype TEXT, nnum INTEGER, dopened DATE, dclosed DATE)')
cursor.execute('CREATE TABLE events (evid INTEGER PRIMARY KEY, nid INTEGER, event TEXT, special INTEGER, sequence INTEGER)')
