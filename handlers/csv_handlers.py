
import cStringIO
import csv
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from models import Student, GradeEntry
import utils
import webapp2


class BulkStudentImportAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if len(self.request.get("remove_all_students")) > 0:
      utils.remove_all_students(user)
    imported_file = self.request.params["bulk-import-file"].value
    process_roster(imported_file, user)
    self.redirect(self.request.referer)

def process_roster(imported_file, user):
  try:
    csv_file = cStringIO.StringIO(imported_file)
    # Read the first kb to ensure the file is a valid CSV file.
    csv.Sniffer().sniff(csv_file.read(1024), ",")
    csv_file.seek(0)
    reader = csv.DictReader(csv_file, dialect="excel")
  except:
    raise Exception("Invalid CSV file")
  reader.fieldnames = [re.compile('[\W_]+', flags=re.UNICODE).sub('', field).lower()
                       for field in reader.fieldnames]
  for row in reader:
    rose_username = row.get("username", None)
    new_student = Student(parent=utils.get_parent_key(user),
                          id=rose_username,
                          first_name=row.get("first", None),
                          last_name=row.get("last", None),
                          team=row.get("team", None),
                          rose_username=rose_username)
    new_student.put()


class ExportCsvAction(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    export_student_name = len(self.request.get("student_name")) > 0
    export_rose_username = len(self.request.get("rose_username")) > 0
    export_team = len(self.request.get("team")) > 0
    urlsafe_assignment_keys = self.request.get_all("assignment_keys[]")
    csv_data = get_csv_export_lists(user, export_student_name, export_rose_username,
                                    export_team, urlsafe_assignment_keys)
    self.response.headers['Content-Type'] = 'application/csv'
    writer = csv.writer(self.response.out)
    for csv_row in csv_data:
      writer.writerow(csv_row)

def get_csv_export_lists(user, export_student_name, export_rose_username,
                         export_team, urlsafe_assignment_keys):
  table_data = []
  student_row_index_map = {} # Map of student_key to row in the table_data
  assignment_col_index_map = {} # Map of assignment_key to column in the table_data
  header_row = []
  table_data.append(header_row)
  num_columns = 0

  # Student Header
  if export_student_name:
    header_row.append("First")
    header_row.append("Last")
    num_columns += 2
  if export_rose_username:
    header_row.append("Username")
    num_columns += 1
  if export_team:
    header_row.append("Team")
    num_columns += 1

  # Assignment Prep
  assignment_keys = []
  for urlsafe_assignment_key in urlsafe_assignment_keys:
    assignment_keys.append(ndb.Key(urlsafe=urlsafe_assignment_key))
  assignments = ndb.get_multi(assignment_keys)
  assignments.sort(key=lambda assignment: assignment.name)
  num_assignments_found = 0
  for assignment in assignments:
    if assignment:
      header_row.append(assignment.name)
      assignment_col_index_map[assignment.key] = num_columns
      num_columns += 1
      num_assignments_found += 1

  # Student Data + assignment placeholders
  num_rows = 1
  students = Student.query(ancestor=utils.get_parent_key(user)).order(Student.rose_username)
  for student in students:
    current_row = []
    if export_student_name:
      current_row.append(student.first_name)
      current_row.append(student.last_name)
    if export_rose_username:
      current_row.append(student.rose_username)
    if export_team:
      current_row.append(student.team)
    for i in range(num_assignments_found):
      current_row.append("-")
    table_data.append(current_row)
    student_row_index_map[student.key] = num_rows
    num_rows += 1

  # Add the grades
  grade_query = GradeEntry.query(ancestor=utils.get_parent_key(user))
  for grade in grade_query:
    if grade.student_key in student_row_index_map and grade.assignment_key in assignment_col_index_map:
      row = student_row_index_map[grade.student_key]
      col = assignment_col_index_map[grade.assignment_key]
      table_data[row][col] = grade.score

  # Removing rows with no grades (allows for data merging)
  for row_index in reversed(range(1, num_rows)):
    row = table_data[row_index]
    blank_grades = row.count("-")
    if blank_grades == num_assignments_found:
      table_data.remove(row)

  return table_data
