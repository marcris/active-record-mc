#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# origActiveRecord.py
#
# The MIT License (MIT)
#
# Copyright (c) 2020 Chris Brown
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
This module is derived from a working example of the active record pattern created to supplement a talk given by Chris
Mitchell at the Oregon Academy of Sciences meeting on January 26, 2011.

The example is published on GitHub as https://github.com/ChrisTM/Active-Record-Example-for-a-Gradebook and the code is
understood to be freely available.
"""

import apsw
# This module uses the apsw interface to SQLite rather than the sqlite3 or pysqlite2 modules.
# (APSW stands for Another Python SQLite Wrapper)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk  # needed in ActiveRecord.error_box

import common  # items of use throughout the program

import logging

logging.basicConfig(level=logging.DEBUG)



class ActiveRecord(object):
    """
    This superclass allows children AR classes to automatically get working
    generic methods like get(), all(), save(), etc, if they define the class
    variables describing the relevant table.

    These class variables are _table_name and _column_names.
    _table_name is simply the name of the table in the database, _column_names
    is a list of the columns that should be part of the active record pattern.

    For the purposes of the current project, child classes will be created by
    calling class_for_table(klass_name, table_name). The child class klass_name
    will be created with attributes _table_name set to table_name and _column_names
    set to an empty list []. The __init__ will fill the column_names list with
    column names obtained by introspection of the database.

    Allowance is made for the usage originally intended where the child class is
    explicitly declared and the class variables explicitly declared and set.

        Example: Student(first_name="Alan", last_name="Turing")

    after Student has been declared as a subclass of ActiveRecord with

        class Student(ActiveRecord):
            _table_name = 'student'
            _column_names = ['first_name', 'last_name', .....]

    Remember that this implementation of AR expects the primary key column
    of a table to be named 'pk'.
    """


    @staticmethod
    def error_box(parent, message_text):
        print(message_text)
        message = gtk.MessageDialog(parent, gtk.DialogFlags.MODAL, gtk.MessageType.ERROR, gtk.ButtonsType.OK)
        message.set_markup('<span size="xx-large" weight="heavy">Database Error</span>')
        message.format_secondary_text(message_text)
        message.run()
        message.destroy()

    def __init__(self, **kwargs):
        """
        Create a new active record instance with the provided properties.
        """
        cls = type(self)
        db = apsw.Connection(cls._db_filename)
        cls._cursor = db.cursor()

        if not self._column_names:
            cls._cursor.execute(f'PRAGMA TABLE_INFO({self._table_name})')
            columns = cls._cursor.fetchall()
            for column in columns:
                self._column_names.append(column[1])    # content of the 'name' column
                if column[5]:   # content of the 'pk' column
                    print('primary key is {}'.format(column[1]))
                    self.__class__._pk = column[1] # primary key column name is class variable

        # Set an attribute for each column to its content in this instance (row)
        for column in self._column_names:
            setattr(self, column, kwargs.get(column))
        self._in_db = False


    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.__class__._pk)

    @classmethod
    def _from_row(cls, row_dict):
        """
        A convenience method for instantiating instances of an AR class
        from a row object from the database. The instance is automatically
        tagged as coming from the database.
        """
        obj = cls(**row_dict)
        obj._in_db = True
        return obj

    @classmethod
    def get(cls, pk):
        """Get a single AR instance for the row with the given pk"""
        query = f"SELECT * FROM {cls._table_name} WHERE {1}=? LIMIT 1".format(cls._table_name)
        try:
            cls._cursor.execute(query, (pk, ))
            row = cls._cursor.fetchone()
            obj = cls._from_row(row)
            return obj
        except apsw.Error as e:
            print(e)
            ActiveRecord.error_box(e.message)
            return None

    @classmethod
    def where(cls, **kwargs):
        """
        Like .all(), but one can add conditions to filter the results.

        Example: Grade.where(points=0)
        """
        # try:
        items = list(kwargs.items())
        columns = list(kwargs.keys())
        values = list(kwargs.values())
        sql_conditions = '=? and '.join(columns) + '=?'
        query = f"SELECT * FROM {cls._table_name} WHERE {sql_conditions}"
        # query = "SELECT * FROM fred WHERE {1}".format(cls._table_name, sql_conditions)
        try:
            cls._cursor.execute(query, values)
            rows = cls._cursor.fetchall()
            objs = [cls._from_row(dict(list(zip(cls._column_names, row)))) for row in rows]
            return objs
        except Exception as e:
            cls.error_box('SQLite error: %s' % (' '.join(e.args)))

    @classmethod
    def all(cls, where="", order=None):
        """
        Return a list of AR instances; one for each row in the table.

        A "WHERE" clause can be added to the SQL "SELECT" by passing in a
        non-null string.

        The facility to specify the ordering of the returned instances by
        a class variable used to generate an "ORDER BY" clause has been
        removed as unnecessary. In the current project the returned instances
        are sorted using a GtkTreeModelSort.
        """

        query = f"SELECT * FROM {cls._table_name}"
        # query = "SELECT * FROM fred".format(cls._table_name)
        try:
            cls._cursor.execute(query)
            rows = cls._cursor.fetchall()
            objs = [cls._from_row(dict(list(zip(cls._column_names, row)))) for row in rows]
            return objs
        except apsw.Error as e:
            # print('SQLite error: %s' % (' '.join(e.args)))
            cls.error_box(None, 'SQLite error: %s' % (' '.join(e.args)))
            return []

    def save(self):
        """
        Save a (new or modified) AR instance into the database.

        Note this is dealing with an AR **instance** representing a row in the database.
        It is therefore an instance method, not a class method.
        """
        if self._in_db:  # already in database; this is an update
            print("updating a record")
            sql_attributes = '=?, '.join(self._column_names) + '=?'
            query = f"UPDATE {self._table_name} SET {sql_attributes} WHERE {self._pk + '=?'}"
            values = [getattr(self, attr) for attr in self._column_names]
            values.append(getattr(self, self._pk))
            logging.debug(str(query) + "; " + str(values))
            try:
                self._cursor.execute('begin')
                self._cursor.execute(query, values)
            except apsw.Error as e:
                self._cursor.execute('rollback')
                raise Exception(e.args[0] + '\n\nThe record has not been updated')
            else:
                self._cursor.execute('commit')
        else:  # not currently in database; this is an insertion
            print('Inserting a record')
            columns = ', '.join(self._column_names)
            placeholders = ', '.join(['?'] * len(self._column_names))
            query = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
            values = [getattr(self, attr) for attr in self._column_names]
            logging.debug(str(query) + "; " + str(values))
            try:
                self._cursor.execute('begin')
                self._cursor.execute(query, values)
                self._in_db = True  # now it **is** in the database
                self.pk = self._cursor.getconnection().last_insert_rowid()
            except apsw.Error as e:
                self._cursor.execute('rollback')
                raise Exception(e.args[0] + '\n\nThe record has not been inserted')
            else:
                self._cursor.execute('commit')

    def modify(self, **kwargs):
        """
        Change the contents of specified field(s) (only) in the row

        Note this is dealing with an AR **instance** representing a row in the database.
        It is therefore an instance method, not a class method.
        """
        columns = list(kwargs.keys())
        placeholders = ', '.join(['?'] * len(columns))
        values = list(kwargs.values())
        sql_attributes = '=? and '.join(columns) + '=?'
        query = "UPDATE {} SET {} WHERE {}=?".format(self._table_name, sql_attributes, placeholders, self.pk)
        values = values + [self.pk]
        logging.debug(str(query) + "; " + str(values))
        try:
            self._cursor.execute('begin')
            self._cursor.execute(query, values)
            self._in_db = True  # succeeded, so it must be in the database
            self.pk = None
        except apsw.Error as e:
            self.error_box(e.message + '\n\nThe record has not been modified.')
            self._cursor.execute('rollback')
        else:
            self._cursor.execute('commit')

    def delete(self):
        """
        Delete the corresponding row from the database
        """
        if self._in_db:  # check the row is present
            query = 'DELETE FROM {0} WHERE pk=?'.format(self._table_name)
            args = (self.pk, )
            try:
                self._cursor.execute('begin')
                self._cursor.execute(query, (self.pk,))
                self._in_db = False  # now it definitely **isn't** in the database
                self.pk = None
            except apsw.Error as e:
                self.error_box(e.message + '\n\nThe record has not been deleted.')
                self._cursor.execute('rollback')
            else:
                self._cursor.execute('commit')
        else:
            print("not _in_db")


def class_for_table(db_filename, klass_name, table_name):
    """
    A function to generate and return a descendant of the ActiveRecord class named for
    klass_name and with
        - table_name
        - an empty list of column names
        - a database integer key, initialised to 0
    as attributes. The initialisation (see above) of an instance of this subclass will
    obtain the relevant column names by introspection of the database. The column name
    of the primary key is assumed to be _pk, and substituted wherever required in the
    generated SQL.
    """
    print(f'class_for_table {db_filename}')
    return type(klass_name, (ActiveRecord,),
                {'_db_filename': str(db_filename),
                 '_cursor': None,
                 '_table_name': table_name,
                 '_column_names': [],
                 '_pk': 0}
                )


def main():
    return 0


if __name__ == '__main__':
    main()
