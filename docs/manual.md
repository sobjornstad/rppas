Introduction
============

The *Records Project Paper Augmentation System* (RPPAS) is a simple
terminal-based program to simplify searching through large numbers of paper
notebooks. It is specifically designed for the way I use my notebooks, but might
be useful to others either to use directly or as a starting point for
customization to meet their own requirements.

Features
========

The main functions of the RPPAS are built around an index, which stores
*notebook types*, *notebook numbers*, and *page numbers* along with *entries* or
keys. For example:

    RPPAS, CB16.57

You can add entries, search for them, edit them, delete them, and combine them.
Each entry can have several occurrences -- you might want to mention the RPPAS
in several places throughout your notebooks. The software handles adding
additional occurrences automatically; if you add the same entry again but with a
different page number, they will be combined.

You can also store the dates during which you have used each notebook and, for
journals, keep track of events that occurred during those dates.

There is also a way to import from CSV, and a similar export feature (for
printing the index or doing anything else with it) is planned.

Setup and running
=================

1. Download the latest version of the software.
2. Copy the default configuration file **config.py.DEFAULT** to a new file
   called **config.py**.
3. Edit config.py in your favorite text editor and set the options as
   appropriate. Note that 'CB' is treated as a special type (journals, with the
   events feature) and should not be changed.
4. Create a new, blank database by running the Python script
   **tools/create\_database** and provide the filename you specified as
   DATABASE_FILENAME in the configuration file. (You can, of course, rename it
   later.) If there are any problems with your sqlite setup, you should find out
   here.
5. Start up the software using the **runrpi** command in the main directory.

If at any time you experience issues with RPPAS, you can always quit the program
by pressing Ctrl-C; RPPAS will save any pending changes to the database before
quitting.

Terminology
===========

This is a brief list of the terminology that is used throughout this manual, the
program, and the source code and database schema.

- **Notebook Type**: A brief name for a sort of notebook. I have CB (Chrono
  Book), TB (Topic Book), and DB (Dream Book) set up; you can configure these in
  config.py, although CB is currently hard-coded to behave differently with the
  events feature. Along with the notebook number, this uniquely identifies a
  notebook. These should be short, since they have to be written at the
  beginning of every reference to a location.
- **Notebook Number**: This is a sequential number unique for all notebooks of a
  given type. You can theoretically select any number when you add a new
  notebook, but for best results, you should start with 1 and pick the the next
  available number when adding a new notebook. You probably want to label your
  actual physical notebooks with these numbers as well. Along with the notebook
  type, this uniquely identifies a notebook.
- **Notebook**: This corresponds exactly with one paper notebook. It is
  identified by a *type* and *number*. Notebooks also have open and close dates,
  representing the dates between which you were still adding new things to the
  notebook, which are displayed in a number of places throughout the program.
  All events and occurrences have an associated notebook.
- **Event**: An event is a description of something that happened during the
  period that a CB (i.e., journal) was open. Events are displayed in the events
  screen for a given notebook and can also be searched through.
- **Special**: A special is an event in all respects except for being listed in
  a different section of the events screen. This is intended to be used for
  particularly salient points in the notebook which are important enough to
  merit a space in the table of contents.
- **Reference Number**: A sequential number displayed to the left of a list of
  entries or events in various places throughout the software. The numbers are
  determined at the time they are displayed (and thus could change if the same
  or similar data is displayed again). Reference numbers are used to select the
  items when you want to perform some action on them.
- **Entry**: An entry is an index "key", such as 'RPPAS', 'violin, practice', or
  'entry, in index'. Each entry is associated with one or more occurrences.
- **Occurrence**: An occurrence is an index "value", indicating one of the
  locations at which the information associated with an entry is to be found
  (such as 'CB2.45'). An occurrence has an associated entry, notebook, and page
  number. There can be several occurrences for a given entry, but each
  occurrence corresponds to only one entry; if the same location is given
  multiple entries, there will be multiple occurrences that are identical except
  for the entry they are associated with.

The relationship between entries and occurrences can be somewhat confusing.
Fortunately, the exact definition of each is mostly an academic point from the
view of the user; since we don't naturally think of indexes in terms of their
entries and occurrences, the program takes care of creating, deleting, and
editing entries and occurrences in the background when changes are made to the
index using higher-level operations such as "add 'RPPAS' on page 23 in notebook
CB5" or "combine the entries 'hello' and 'hi'". However, it is still useful to
be able to distinguish between them on a surface level. For example, in the
following output...

    RPPAS: CB13.45, TB2.158

...we can say that the *entry* **RPPAS** has two *occurrences*: **CB13.45** and
**TB2.158**.


Working with notebooks
======================

In order to start using RPPAS, you need to have at least one notebook. You can
access the notebooks screen by pressing 'n' on the main screen. You can return
to the main screen by quitting ('q') from the notebooks screen.

The notebooks screen displays a list of books (type + number) and the open and
close dates of each.

Editing the list of notebooks
-----------------------------

The options add, edit, and delete should be fairly self-explanatory (edit just
allows you to change the dates). When you're done making changes, choose 'save
changes.' Choosing 'undo changes' will roll back all changes you've made since
the last save.

Filtering the list of notebooks
-------------------------------

There are three options for filtering, listed below the line in the commands
box:

- **Filter** asks for "opened after" and "closed before" dates and shows
  notebooks that match those criteria. The dates must be valid, but may be
  anywhere within the VALID\_DATE\_RANGE defined in the configuration file,
  regardless of whether there are any notebooks that have that date.
- **Open at time** asks for a date and displays all notebooks that were open on
  that date (that is, were closed after that date but opened before it).
- **Clear filter** cancels any filters that are currently active and displays
  all notebooks.

You may only have one filter active at a time; specifying a second filter will
cancel any currently active filter.

The events screen
-----------------

The events screen is a special screen accessible for notebooks of type 'CB'
(that is, Chrono Books, or journals). Pressing 'v' to open the events screen
will ask for the number of a CB to view. After you enter a number, the events
screen will display the notebook type and number, the dates during which it was
open, and lists of events and *specials*. Specials and normal events are alike
in all ways except for being displayed under two different headings.

The numbers to the left of events are provided for reference when deleting or
repositioning only and have no further significance.

- **Add** allows you to add a new event. You'll be asked for the description and
  whether or not it is a special, and it will be added to the end of the list.
  If you want to move it somewhere else, you can use *reposition*.
- **Delete** deletes an event from the list and moves the other events up to
  fill the gap.
- **Reposition** allows you to swap two events or two specials (but you can't
  switch an event from one to the other with this option). You'll be asked for
  the numbers of each.
- **Save** and **Undo** work the same as they do when editing notebooks. (Be
  careful with undo; if you haven't been saving your changes, it may undo the
  addition of quite a few events.)
- **Change book** allows you to specify another CB to jump to and show events
  for. For example, if you're viewing CB13 and you decide you want to see the
  events for CB2, you can use this to move there without having to quit out of
  the events screen and open the events screen again.
- **Next book** and **Previous book** are further shortcuts to move to the
  numbered book immediately after and immediately before the current one. They
  work exactly the same way as *Change book*.

If you make a typo when adding an event, you can delete the entry and add it
again.

Quitting from the events screen returns you to the notebooks screen.

Adding entries
==============

Once you've added at least one notebook to put entries into, you can start
adding entries. When you add entries by pressing the 'a' key on the main screen,
you'll be asked for a type and number to add to. After selecting a valid
notebook, you'll be prompted for an *entry*. All entries are added to the
notebook you specified at the beginning in order to avoid requiring a lot of
typing; if you want to add to another notebook, you can quit and open the adding
screen again.

Almost anything is valid as an entry, but sticking to traditional index syntax
is recommended. Examples:

- RPPAS
- winter clothing, making people unrecognizable
- violin, practice
- gender, of software

In order to maintain useful alphabetization, I also use the convention of
placing both quotation marks and underscores at the end of entries; for example:

- camouflage"", spelling of
- The West Wing\_\_

I would implement a sort that ignored those characters, but unfortunately this
is handled by SQLite and I don't want to try to figure out how to change the
sort there. So for now I use the workaround and hopefully this will be better in
the indeterminate future.

After entering an entry, you'll be prompted for a *page*. You can technically
put anything in the page field, but for best results, the following options are
recommended:

- A reference to another entry: **see FOO**
- A single page number: **34**
- A series of page numbers: **34, 55, 171**
- A range: **34-36**

If you enter a range and one or both of the pages is fewer digits than the
maximum number of digits that is possible for that notebook type (for instance,
in a notebook type with 80 pages, just one digit, or in a notebook type with 240
pages, one or two digits), in order to ensure you can search for and sort the
range as effectively as possible, you need to make sure to pad them with leading
zeroes. For instance, in an 80-page notebook, **5-10** becomes **05-10**, and in
a 240-page notebook, **50-71** becomes **050-071**. You don't have to worry
about this when entering single pages or comma-separated page numbers; the
software will take care of it automatically.

When you press Enter, RPPAS will place that entry into the *queue* along with
the page number needed to create occurrences later, then prompt you for another
entry. (If you enter multiple page numbers, RPPAS will automatically create
multiple occurrences and place all of them in the queue.) You can keep typing as
many entries as you want; RPPAS will automatically save the queue in the
background after it reaches five entries, so that you don't lose any data in the
event of a power failure or crash. You can view the contents of the queue with
the adding command */queue*; see the following section.

If you specify an entry that already exists in the database, RPPAS will add the
page and notebook numbers you provided to that entry (in technical terms, it
will add new occurrences to the existing entry). If you enter exactly the same
entry *and* the same page number, RPPAS will silently ignore your entry.


Adding commands
---------------
Instead of an entry, you can also type an *adding command*. Adding commands
begin with a slash (/) and are accepted anywhere you are prompted for an entry
(but not when prompted for a page -- then it will cheerfully enter the adding
command as the page number of the previous entry).

Valid adding commands:

- **/help**: Show the list of adding commands and a brief description of each,
  for quick reference.
- **/queue**: Display the entries that are currently in the queue -- that is,
  any that have been entered but not yet saved to disk. This is useful in
  combination with the */strike* command to see what you're going to undo.
- **/save**: Immediately save the contents of the queue to disk, rather than
  waiting for an automatic save.
- **/history**: Show a list of all the entries you've added this session, along
  with anything still in the queue. Be careful, as this might be very large if
  you've added many things this session.
- **/strike**: Delete the last entry (if you made a typo or other mistake). You
  can optionally /strike multiple entries at once by providing the number of
  added entries to remove, e.g., */strike 3*. If the entry(ies) have left the
  queue and been saved to disk, the strike will take a moment to complete, as
  the entry has to be updated on disk instead of simply removed from the queue.
- **/quit**: Save any entries remaining in the queue and return to the main
  menu.

Searching
=========

Once you've created some notebooks and added some entries to them, the real fun
begins with searching through the entries. You can open the search screen by
pressing 's' on the main screen.

The search searches substrings, so "foo," "bar," "foobar," or even "oob" would
match the entry "foobar". Searches are not case-sensitive.

Once you've entered a search, you'll be shown a list of all matching entries,
with reference numbers in front of them. (If there aren't any results, it will
instead display "no results.")

If you're not satisfied with the results, you can try entering your search again
or try different search terms by pressing 's' again.

Many commands on this screen print their output at the bottom of the screen;
once you've used enough of them, it may get cluttered or even full enough to
push the results off the top of the screen. If at any time you'd like to return
to displaying just the results, you can choose Reload ('r').

Filtering
---------

If a search returns too many results, you can *filter* it by pressing 'f' and
specifying another substring that you additionally want to be present in the
result. These substrings can overlap, and you can include as many as you want,
so an initial search of "foo" followed by a filter on "bar" would find *foobar*
but not *foob*, as would a search for "foo" and a filter for "oba".

Filters, once activated, are displayed underneath the search query at the top of
the screen. You can clear all filters (but retain your original search) by
selecting the Unfilter ('u') option. If you start a completely new search by
pressing 's', all filters are automatically cleared.

Looking up results
------------------

You can find the occurrences of a given entry (that is, find the locations at
which the information described by that entry is to be found) using the *lookup*
command, accessed with the 'l' (lowercase L) key. You'll be prompted for the
reference number located to the left of the appropriate entry, and RPPAS will
print out the entry followed by a list of all its occurrences.

Since many searches return only a few results and it's common to look up a
number of entries, RPPAS allows you to save a few keystrokes by simply pressing
the number without selecting 'l' first, as long as the number is only one digit.
So pressing simply '4' is equivalent to choosing 'l', then typing '4' and
pressing Enter. Of course, if the number of the entry you want to look up is
more than one digit, you must press 'l' first, or looking up 14 would result in
looking up number 1, then looking up number 4.

Nearby
------

Sometimes the meaning of an index entry might turn out to be less than clear a
year or five later, or there might be a number of occurrences that could be what
you're looking for, but from just the numbers it's kind of difficult to tell.
When you only have one or two notebooks, it's easy enough to just check the
possibilities, but when you have more than a few, it starts to get unwieldy to
look up all the possible references. For this reason, RPPAS provides the
*nearby* and *when was* features to give you a chance at working out which
occurrence you want before actually looking it up. The idea of Nearby is that
seeing a few other index entries associated with that page or nearby pages might
be enough to jog your memory. In my experience, this works surprisingly well.

In order to use the Nearby function, you need the notebook type and number and
the page number. This information should not be very difficult to find; if you
haven't done so already, you can find it by doing a lookup on the appropriate
entry.

After entering the information, you'll be given a list of entries that have
occurrences on the page number you entered or the one right before or after it.
In many ways this is like a reverse lookup: the occurrences are found and the
entries associated with them displayed.

If you want to look a little bit further forward or backward than *nearby*
provides you with, you can always re-run the nearby command on a page number
slightly higher or lower than your original entry.

When was
--------

Another feature to make it easier to see what an entry and occurrence is
referring to without going and finding the notebook is the *when was* feature.

When Was simply pulls up the events screen for the appropriate CB, providing
context in the form of a range of dates between which you might have written the
occurrence and some events that took place during that time. (This feature only
works with CBs at the moment; in the future, I intend to support at least
showing the dates for other types of notebooks, even though an events screen
doesn't exist for them.) You can move around and look at other events screens as
you would normally; when you quit from this screen, you will be returned to the
search results page.

Searching events
----------------

It may be productive to search through the events of all of your notebooks as
well as the index entries. You can easily search events by pressing 'v' from the
search screen. This will start the event search viewer on the current search
query.

Once in the event search viewer, you can search the text of events for something
else using the 's' key, if you wish; this will *not* change the search "up one
level" on the main search screen, which will be restored when you quit.

Running 'lookup' on one of the results will take you to the events screen where
the listed event appears. Pressing quit from there returns you to the event
search screen. (Currently there is a bug here where two events that have the
same name make it impossible to look up either.) As on the main search screen,
you can look up events with a single-digit number by simply pressing the number.

Editing entries
---------------

Entries are edited from the search screen, by pressing the 'e' key and entering
the entry's reference number. There are three options:

- **Fix entry**: Change the text of the entry, leaving all the occurrences
  unchanged. This is useful if you discover that you've made a typo in the name
  of an entry.
- **Coalesce entry**: Merges the occurrences of one entry into another entry.
  For example, if you have the entry **hello** with the occurrence 'CB2.45'
  and the entry **hi** with the occurrence 'TB1.213' and you edit the entry
  **hello**, coalescing it into **hi** will result in the single entry **hi** with
  the occurrences 'CB2.45' and 'TB1.213'. You can optionally leave a redirect
  behind under the old entry's name, which will say "moved to OTHER\_ENTRY\_NAME".
  This is useful if you discover that you've written two slightly differently
  worded index entries in different notebooks that really refer to exactly the
  same thing.
- **Delete entry**: Deletes the entry and all of its occurrences. This cannot be
  undone (except by restoring a backup). This should rarely be needed, but is
  provided for completeness.


Importing
=========

The Import ('i') option on the main menu allows you to import an index from a
tab-separated file (the delimiter can be easily changed in the source code if
you wish).

The file should have five columns:

- An ID number for this line. This is not actually used, so can contain anything
  as long as it is a column (in other words, there is a tab after it).
- A notebook type (e.g., 'CB').
- A notebook number.
- A page number or numbers. This will be dropped directly into the page field,
  but should preferably follow the recommended format laid out in the "Adding
  entries" section of this manual.
- The entry.

In order to match the previous format I used and a more common method of writing
indexes, this doesn't have entries and occurrences in quite the same way that
RPPAS has. It can handle multiple occurrences within the same notebook on the
same line, but if there are occurrences across several notebooks, each notebook
needs to be on a new line with the same entry value.
