# TreeViewDbExample.py
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

import os
import sys

from ActiveList import TVColumn, ActiveList
import ActiveRecord
print(f'ActiveRecord from {ActiveRecord.__file__}')


# TreeModel column ID's
COL_SEQ,\
COL_LAST,\
COL_FIRST,\
COL_TITLE,\
COL_BOSS,\
COL_BORN,\
COL_HIRED,\
COL_SORT,\
COL_KEY = range(9)


class TV(ActiveList):
    # The ActiveList defines the columns for the treeview
    _columns = [
        # The following column (column 0) contains a string representing a
        # background colour to be used for the whole row.
        TVColumn(COL_SEQ, str)

        # The following columns are obtained from the source
        # and displayed in the treeview.

        # column 1 (LastName)
        , TVColumn(COL_LAST, str, "LastName", 75, COL_SEQ, gtk.CellRendererText)
        # column 2 (FirstName)
        , TVColumn(COL_FIRST, str, "FirstName", 75, COL_SEQ, gtk.CellRendererText)
        # column 3 (Title)
        , TVColumn(COL_TITLE, str, "Title", 93, COL_SEQ, gtk.CellRendererText)
        # column 4 (Reports To)
        , TVColumn(COL_BOSS, int, "ReportsTo", 75, COL_SEQ, gtk.CellRendererText)
        # column 5 (BirthDate)
        , TVColumn(COL_BORN, str, "Born", 70, COL_SEQ, gtk.CellRendererText)
        # column 6 (HireDate)
        , TVColumn(COL_HIRED, str, "Hired", 70, COL_SEQ, gtk.CellRendererText)

        # The following source fields are used but not displayed

        # KEY - e.g. database key to identify a record for UPDATE etc
        , TVColumn(COL_KEY, int)
    ]


class MyWindow(gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(title="TreeView Example", application=app)
        self.set_default_size(250, 250)

        self.treeview = gtk.TreeView()
        self.create_model_and_view_columns(f'{os.path.dirname(__file__)}/chinook.db')
        # self.add(self.treeview)

    def create_model_and_view_columns(self, filepath):
        my_TV = TV(self.treeview)  # an instance of our descendant of ActiveList which
        # defines the model and the columns of the treeview
        self.treeview.set_model(my_TV.model)

        # The following code gets the data from some source (an SQLite database),
        # and loads it into the treeview's model (storage).

        # Put the name of the source (SQL query) as the window title
#        self.set_title("Employee.where(Title='IT Staff')")
        self.set_title("Employee.all()")

        employees_class = ActiveRecord.ActiveRecord.class_for_table(filepath, "Employees", "employees")

        r = employees_class()  # make a new instance of the class
        print('List all the employees')
        rows = r.all()
        for row in rows:
            print(f'{row.FirstName} {row.LastName}  {row.Title}')

        print('Create a new record for Joe Bloggs as Personnel Manager')
        s = employees_class()  # make a separate instance of the class
        s.LastName = 'Bloggs'
        s.FirstName = 'Joe'
        s.Title = 'Personnel Manager'
        s.ReportsTo = 1
        s.BirthDate = '1943-08-25'
        s.HireDate = '2002-09-04'
        s.save()

        print('List all the employees with LastName=Bloggs')
        print('to prove we successfully added the record')
        rows = r.where(LastName='Bloggs')
        for row in rows:
            print(f'{row.FirstName} {row.LastName}  {row.Title}')

        print('Change his FirstName to Fred, a full record update')
        rows[0].FirstName = 'Fred'
        rows[0].save()

        print('List all the employees')
        print('to show the change was made')
        rows = r.all()
        for row in rows:
            print(f'{row.FirstName} {row.LastName}  {row.Title}')

        print('Change Laura Callahan\'s title to Sales Support Agent')
        print('(a specific fields only modification) ...')
        rows = r.where(LastName='Callahan')
        rows[0].modify(Title='Sales Support Agent', ReportsTo=2)

        print('... and demonstrate the change was made')
        rows = r.where(LastName='Callahan')
        for row in rows:
            print(f'{row.FirstName} {row.LastName}  {row.Title}')

        print('Delete all reference to ... Bloggs')
        rows = r.where(LastName="Bloggs")
        for row in rows:
            row.delete()

        print('Show that we now have the original records, and only those')
        print('(except Laura\'s changed job title)')
        rows = r.all()
        for row in rows:
            print(f'{row.FirstName} {row.LastName}  {row.Title}')


        self.add(self.treeview)
        self.show_all()



class MyApplication(gtk.Application):

    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.window = MyWindow(self)

    def do_startup(self):
        # start the application
        gtk.Application.do_startup(self)


app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
