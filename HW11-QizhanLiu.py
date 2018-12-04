#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from collections import defaultdict
from prettytable import PrettyTable
import sqlite3

DB_FILE = 'C:/810/assignments/810_startup.db'
db = sqlite3.connect(DB_FILE)


class Student:
    # students will have attributes：cwid, name, major and courses
    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.courses = defaultdict(str)
        self.pass_courses = list()
        self.rem_req = set()
        self.rem_ele = set()
        self.pass_course()

    def get_course(self, course, grade):
        self.courses[course] = grade

    def pass_course(self):
        for course in self.courses.keys():
            if self.courses[course] != 'F':
                self.pass_courses.append(course)
        return self.pass_courses


class Instructor:
    # instructor will have attributes：cwid, name, department and courses
    def __init__(self, cwid, name, depart):
        self.cwid = cwid
        self.name = name
        self.depart = depart
        self.courses = defaultdict(int)

        # add_student, get courses, get student_cnt

    def add_student(self, course):
        self.courses[course] += 1

    def get_course(self):
        return self.courses.keys()

    def get_student_cnt(self, course):
        return self.courses[course]


class Grade:

    def __init__(self, stu_cwid, course_name, score, ins_cwid):
        self.stu_cwid = stu_cwid
        self.score = score
        self.course_name = course_name
        self.ins_cwid = ins_cwid


class Major:

    def __init__(self, dept):
        self.dept = dept
        self.r_courses = set()
        self.e_courses = set()

    def add_course(self, flag, course):
        if flag == 'R':
            self.r_courses.add(course)
        elif flag == 'E':
            self.e_courses.add(course)
        else:
            raise ValueError('Invalid flag')


def read_file(path):
    try:
        fp = open(path)
    except FileNotFoundError:
        print("File doesn't exist.")
    else:
        with fp:
            for line in fp:
                yield tuple(line.strip().split('\t'))


class Repository:

    def __init__(self):
        self.stu_filename = 'students.txt'
        self.ins_filename = 'instructors.txt'
        self.gra_filename = 'grades.txt'
        self.maj_filename = 'majors.txt'
        self.students = dict()
        self.instructors = dict()
        self.majors = dict()
        self.read_students()
        self.read_instructors()
        self.read_grades()
        self.read_majors()

    def read_students(self):
        stu_file = read_file(self.stu_filename)
        for cwid, name, major in stu_file:
            self.students[cwid] = Student(cwid, name, major)

    def read_instructors(self):
        ins_file = read_file(self.ins_filename)
        for cwid, name, dept in ins_file:
            self.instructors[cwid] = Instructor(cwid, name, dept)

    def read_grades(self):
        gra_file = read_file(self.gra_filename)
        for stu_cwid, course, grade, ins_cwid in gra_file:
            if stu_cwid in self.students.keys():
                self.students[stu_cwid].courses[course] = grade
                if ins_cwid in self.instructors.keys():
                    self.instructors[ins_cwid].courses[course] += 1

    def read_majors(self):
        maj_file = read_file('majors.txt')
        for name, flag, course in maj_file:
            self.majors[name] = Major(name)
        maj_file2 = read_file('majors.txt')
        for name, flag, course in maj_file2:
            self.majors[name].add_course(flag, course)

        for cwid, stu in self.students.items():
            stu.rem_req = self.majors[stu.major].r_courses - set(stu.courses.keys())
            stu.rem_ele = self.majors[stu.major].e_courses - set(stu.pass_course())

    def student_results(self):
        student_summary = PrettyTable(
            field_names=['CWID', 'Name', 'Complete Courses', 'Remaining Required', 'Remaining Electives'])
        for cwid, stu in self.students.items():
            student_summary.add_row([cwid, stu.name, set(stu.pass_course()),
                                     stu.rem_req, str((lambda:stu.rem_ele if len(stu.rem_ele) == 3 else None)())])
        print('Student Summary\n')
        print(student_summary)
        print('\n')

    def instructor_results(self):
        instructor_summary = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Courses', 'Students'])
        for cwid, instructor in self.instructors.items():
            for course in instructor.ins_courses:
                instructor_summary.add_row([cwid, instructor.name, instructor.depart,
                                            course, instructor.ins_courses[course]])
        print('Instructor Summary\n')
        print(instructor_summary)

    def major_results(self):
        major_summary = PrettyTable(field_names=['Dept', 'Required', 'Electives'])
        for name, major in self.majors.items():
            major_summary.add_row([major.dept, major.r_courses, major.e_courses])
        print('Major Summary\n')
        print(major_summary)
        print('\n')


def main():
    # create a stevens Repository
    stevens = Repository()

    stevens.major_results()

    # print student table
    stevens.student_results()

    # print instructor table
    '''stevens.instructor_results()'''

    instructors_summary = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Courses', 'Students'])
    for row in db.execute("select CWID, Name, Dept, Course, count(Student_CWID) from HW11_instructors "
                          "join HW11_grades on CWID = Instructor_CWID group by Course order by CWID"):
        instructors_summary.add_row(row)
    print('Instructor Summary\n')
    print(instructors_summary)


if __name__ == '__main__':
    main()
