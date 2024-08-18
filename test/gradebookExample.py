# gradebookExample.py
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

import sys
import os

from ActiveRecord import ActiveRecord

class MyWindow(gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(title="Gradebook Example", application=app)
        self.set_default_size(250, 100)
        self.show_all()

        self.db_filename = f'{os.path.dirname(__file__)}/gradebook.db'
        print(f'db = {self.db_filename}')

        if not os.path.exists(self.db_filename):
            app.init_db(self.db_filename)

        student_class = ActiveRecord.class_for_table(self.db_filename, "Student", "student")
        assignment_class = ActiveRecord.class_for_table(self.db_filename, "Assignment", "assignment")
        grade_class = ActiveRecord.class_for_table(self.db_filename, "Grade", "grade")
        try:
            r = student_class()    # make an instance of the class
            for student in r.all(order='first_name, last_name, pk'):
                print(student.first_name, student.last_name, student.alias)
                a = assignment_class()
                for asg in a.all(order='-due_date, name, pk'):
                    print(asg.name, asg.due_date, asg.points)
                    g = grade_class()
                    for grade in g.all(where=f'student_pk={student.pk} and assignment_pk={asg.pk}'):
                        print(student.first_name, student.last_name, student.alias, asg.name, asg.due_date, grade.points)

                print('---------------------------------')

        except Exception as e:
            print(e.args)
            ActiveRecord.error_box(self, e.args[0])


class MyApplication(gtk.Application):

    def __init__(self):
        super().__init__()
        self.window = None

    @staticmethod
    def init_db(db_filename):
        """
        Set up the database with instructions from schema.sql and testdata.sql
        """
        import apsw
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))

        db = apsw.Connection(db_filename)
        cursor = db.cursor()
        for filename in [os.path.join(dir_path, "schema.sql"), "testdata.sql"]:
            with open(os.path.join(dir_path, filename)) as f:
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
