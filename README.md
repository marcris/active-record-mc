This module implements a simple ORM for basic operations in SQLite databases.

The module is derived from a working example of the active record pattern created by Chris Mitchell
to supplement a talk given at the Oregon Academy of Sciences meeting on January 26, 2011.

The original example is published on GitHub as

https://github.com/ChrisTM/Active-Record-Example-for-a-Gradebook

and the code is understood to be freely available under the MIT license as above.

The original code has been modified so that

    The column names in the selected table are obtained automatically by introspection of the database.
    The primary key column is no longer required to be 'pk'.
    Errors are reported via a dialog box.

