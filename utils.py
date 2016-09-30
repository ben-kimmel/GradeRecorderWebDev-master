from google.appengine.ext import ndb
from models import Assignment, Student, GradeEntry


def get_parent_key(user):
    return ndb.Key("Entity", user.email().lower())


def get_assignments(user):
    """ Gets all of the assignments for this user and makes a key map for them. """
    assignments = Assignment.query(ancestor=get_parent_key(user)).order(Assignment.name).fetch()
    assignments_map = {}
    for assignment in assignments:
        assignments_map[assignment.key] = assignment
    return assignments, assignments_map


def get_students(user):
    """ Gets all of the students for this user and makes a key map for them. """
    students = Student.query(ancestor=get_parent_key(user)).order(Student.rose_username).fetch()
    students_map = {}
    teams = []
    for student in students:
        students_map[student.key] = student
        if student.team not in teams:
            teams.append(student.team)
    return students, students_map, sorted(teams)


def get_grade_entries(user, assignments_map, students_map):
    """ Gets all of the grade entries for this user.
        Replaces the assignment_key and student_key with an assignment and student. """
    grade_entries = GradeEntry.query(ancestor=get_parent_key(user)).fetch()
    for grade_entry in grade_entries:
        grade_entry.assignment = assignments_map[grade_entry.assignment_key]
        grade_entry.student = students_map[grade_entry.student_key]
    return grade_entries


def remove_all_grades_for_assignment(user, assignment_key):
    """ Removes all grades for the given assignment. """
    grades_for_assignment_query = GradeEntry.query(ancestor=assignment_key)
    for grade in grades_for_assignment_query:
        grade.key.delete()


def remove_all_grades_for_student(user, student_key):
    """ Removes all grades for the given student. """
    grades_for_student_query = GradeEntry.query(GradeEntry.student_key==student_key, ancestor=get_parent_key(user))
    for grade in grades_for_student_query:
        grade.key.delete()


def remove_all_students(user):
    """ Removes all grades and all students for a user. (use with caution) """
    all_grades_query = GradeEntry.query(ancestor=get_parent_key(user))
    for grade in all_grades_query:
        grade.key.delete()
    all_students_query = Student.query(ancestor=get_parent_key(user))
    for student in all_students_query:
        student.key.delete()

