This module implements a simple ORM for basic operations in SQLite databases.

The module is derived from a working example of the active record pattern created by
Chris Mitchell to supplement a talk given at the Oregon Academy of Sciences meeting
on January 26, 2011.

The original example is published on GitHub as

https://github.com/ChrisTM/Active-Record-Example-for-a-Gradebook

and the code is understood to be freely available under the MIT license.

The original code has been modified so that

* The column names in the selected table are obtained automatically by introspection of the database.
* The primary key column is no longer required to be 'pk'.
* Errors are reported via a dialog box.

The modified code is referenced extensively (with Chris Mitchell's permission) in my book
"Programming Python with GTK and SQLite".

Running gradebookExample.py demonstrates queries equivalent to Chris Mitchell's
original tests.

More complex usage in conjunction with active-list-mc is demonstrated in TreeViewDbExampleAll.py. This program requires the Chinook database, see

https://github.com/lerocha/chinook-database

from which it uses the "employees" table.
