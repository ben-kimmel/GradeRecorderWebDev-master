from google.appengine.api import users
from google.appengine.ext import ndb
import utils
import webapp2


class DeleteStudentAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if self.request.get('student_to_delete_key') == "AllStudents":
      utils.remove_all_students(user)
    else:
      student_key = ndb.Key(urlsafe=self.request.get('student_to_delete_key'))
      utils.remove_all_grades_for_student(user, student_key)
      student_key.delete();
    self.redirect(self.request.referer)


class DeleteAssignmentAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    assignment_key = ndb.Key(urlsafe=self.request.get('assignment_to_delete_key'))
    utils.remove_all_grades_for_assignment(user, assignment_key)
    assignment_key.delete();
    self.redirect(self.request.referer)


class DeleteGradeEntryAction(webapp2.RequestHandler):
  def post(self):
    grade_entry_key = ndb.Key(urlsafe=self.request.get('grade_entry_to_delete_key'))
    grade = grade_entry_key.get()
    urlsafe_assignment_key = grade.assignment_key.urlsafe()
    grade_entry_key.delete();
    self.redirect("/?active_assignment=" + urlsafe_assignment_key)

