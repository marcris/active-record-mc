# TreeViewDbExample.py
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

import sys
import os
from pathlib import Path

from origActiveRecord import ActiveRecord, class_for_table

from rich.traceback import install



# class Student(ActiveRecord):
#     _table_name = 'student'
#     _default_order = 'first_name, last_name, pk'
#     _column_names = ['first_name', 'last_name', 'alias']
#
#     @property
#     def full_name(self):
#         full_name = ' '.join([self.first_name, self.last_name])
#         return full_name.strip()
#
#     def get_grades(self):
#         return Grade.where(student_pk=self.pk)
#
#
# class Assignment(ActiveRecord):
#     _table_name = 'assignment'
#     _default_order = '-due_date, name, pk'
#     _column_names = ['name', 'due_date', 'points']
#
#     def get_grades(self):
#         return Grade.where(assignment_pk=self.pk)
#
#
# class Grade(ActiveRecord):
#     # Note how just this table metadata is enough for the superclass to give
#     # us a working active record class
#     _table_name = 'grade'
#     _default_order = 'pk'
#     _column_names = ['student_pk', 'assignment_pk', 'points', 'comment']


class MyWindow(gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(title="gradebook Example", application=app)
        self.set_default_size(250, 100)
        self.show_all()

        file = Path('__file__').resolve()  # db file is in same directory as this source
        # file.parents[0] is our source's containing directory
        self.db_filename = str(file.parents[0]) + '/gradebook.db'
        print(f'db = {self.db_filename}')

        if not os.path.exists(self.db_filename):
            app.init_db(self.db_filename)

        student_class = class_for_table(self.db_filename, "Student", "student")
        assignment_class = class_for_table(self.db_filename, "Assignment", "assignment")
        grade_class = class_for_table(self.db_filename, "Grade", "grade")
        try:
            r = student_class()    # make an instance of the class
            for row_number, student in enumerate(r.all(order='first_name, last_name, pk')):
                a = assignment_class()
                for asg_number, asg in enumerate(a.all(order='-due_date, name, pk')):
                    g = grade_class()
                    for grade_number, grade in enumerate(g.all(where=f'student_pk={student.pk} and assignment_pk={asg.pk}')):
                        print(student.first_name, student.last_name, asg.name, grade.points)

        except Exception as e:
            print(e.args)
            ActiveRecord.error_box(self, e.args[0])

class MyApplication(gtk.Application):

    def __init__(self):
        super().__init__()

        install(show_locals=True)


    def init_db(self, db_filename):
        """
        Set up the database with instructions from schema.sql and testdata.sql
        """
        import apsw
        db = apsw.Connection(db_filename)
        cursor = db.cursor()
        for filename in ["schema.sql", "testdata.sql"]:
            with open(filename) as f:
                cursor.execute(f.read())

    def do_activate(self):
        self.window = MyWindow(self)


    def do_startup(self):
        gtk.Application.do_startup(self)

    def do_shutdown(self):
        gtk.Application.do_shutdown(self)


app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
