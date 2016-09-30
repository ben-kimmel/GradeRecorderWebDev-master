from google.appengine.api import users
from google.appengine.ext import ndb
from models import Student, Assignment, GradeEntry
import utils
import webapp2


class AddStudentAction(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        rose_username = self.request.get('rose_username')
        new_student = Student(parent=utils.get_parent_key(user), id=rose_username, first_name=self.request.get('first_name'), last_name=self.request.get('last_name'), rose_username=rose_username, team=self.request.get('team'))
        new_student.put()
        self.redirect("/")


class InsertAssignmentAction(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        urlsafe_entity_key = self.request.get('assignment_entity_key')
        if len(urlsafe_entity_key) > 0:
            assignment_key = ndb.Key(urlsafe=urlsafe_entity_key)
            assignment = assignment_key.get()
        else:
            assignment = Assignment(parent=utils.get_parent_key(user))
            assignment.name = self.request.get('assignment_name')
        assignment.put()
        self.redirect("/?active_assignment=" + assignment.key.urlsafe())




class AddSingleGradeEntryAction(webapp2.RequestHandler):
    def post(self):
        assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
        student_key = ndb.Key(urlsafe=self.request.get('student_key'))
        student = student_key.get()
        score = int(self.request.get('score'))
        new_grade_entry = GradeEntry(parent=assignment_key, id=student.rose_username, assignment_key=assignment_key, student_key=student_key, score=score)
        new_grade_entry.put()
        self.redirect("/?active_assignment=" + assignment_key.urlsafe())



class AddTeamGradeEntryAction(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
        score = int(self.request.get('score'))
        team = self.request.get('team')
        student_query = Student.query(Student.team == team, ancestor=utils.get_parent_key(user))
        for student in student_query:
            new_grade_entry = GradeEntry(parent=assignment_key, id=student.rose_username, assignment_key=assignment_key, student_key=student.key, score=score)
            new_grade_entry.put()
        self.redirect("/?active_assignment=" + assignment_key.urlsafe())

