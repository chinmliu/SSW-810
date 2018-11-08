#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
Create a program that can list some basic information of students and instructors

using the prettytable module, using class and dictionary

Programmer: Qizhan Liu


"""

from collections import defaultdict
import os
import abc
from prettytable import PrettyTable


class People(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def say(self):
        pass


class Grade:
    def __init__(self, stu_id, course_name, score, instr_id):
        self.stu_id = stu_id
        self.score = score
        self.course_name = course_name
        self.instr_id = instr_id


class Student(People):
    def say(self):
        print('Thank you!')

    def __init__(self, CWID, name, major):
        self.CWID = CWID
        self.name = name
        self.major = major
        self.courses = dict()

    def add_course(self, course_name, score):
        self.courses[course_name] = score


class Instructor(People):
    def say(self):
        print('Thank you!')

    def __init__(self, CWID, name, dept):
        self.CWID = CWID
        self.name = name
        self.dept = dept
        self.courses = defaultdict(int)

    def add_course(self, course_name):
        self.courses[course_name] += 1


class Utils:
    @staticmethod
    def read_line(path):
        try:
            file = open(path)
        except FileNotFoundError:
            raise FileNotFoundError(f'warning: file({path}) not found')
        with file:
            for line in file:
                attr = line.strip().split(f'\t')
                if len(attr) != 0 or attr is not None:
                    yield attr
                else:
                    break
        yield None


class Repository:
    def __init__(self, init_dir):

        # key: student_CWID  value: student
        self.students = dict()

        # key: instructor_CWID  value: instructor
        self.instructors = dict()

        # key: (student_CWID, course_name)  value: grade
        self.grades = dict()
        self.students_path = os.path.join(init_dir, 'students.txt')
        self.instructors_path = os.path.join(init_dir, 'instructors.txt')
        self.grades_path = os.path.join(init_dir, 'grades.txt')
        self.read_student(self.students_path)
        self.read_instructors(self.instructors_path)
        self.read_grades(self.grades_path)

    def read_student(self, path):
        get_result = Utils.read_line(path)
        while True:
            attr = next(get_result)
            if attr:
                student = Student(attr[0], attr[1], attr[2])
                self.students[student.cwid] = student
            else:
                break
        return self.students

    def read_instructors(self, path):
        get_result = Utils.read_line(path)
        while True:
            attr = next(get_result)
            if attr:
                instructor = Instructor(attr[0], attr[1], attr[2])
                self.instructors[instructor.cwid] = instructor
            else:
                break
        return self.instructors

    def read_grades(self, path):
        get_result = Utils.read_line(path)
        while True:
            attr = next(get_result)
            if attr:
                grade = Grade(attr[0], attr[1], attr[2], attr[3])
                self.grades[grade.stu_id, grade.course_name] = grade
            else:
                break
        return self.grades

    def show_students(self):
        student_summary_table = PrettyTable()
        student_summary_table.field_names = ['CWID', 'Name', 'Completed Course']
        for student in self.students.values():
            student_summary_table.add_row([student.cwid, student.name, list(student.Courses.keys())])
        print(student_summary_table.get_string())

    def show_instructors(self):
        instructor_summary_table = PrettyTable()
        instructor_summary_table.field_names = ['CWID', 'Name', 'Dept', 'Course', 'Students']
        for instructor in self.instructors.values():
            for course_name in instructor.courses.keys():
                instructor_summary_table.add_row(
                    [instructor.cwid, instructor.name, instructor.dept, course_name, instructor.courses[course_name]])
        print(instructor_summary_table.get_string())

    def analysis_grades(self):
        for grade in self.grades.values():
            self.students.get(grade.stu_id).add_course(grade.course_name, grade.score)
            self.instructors.get(grade.ins_id).add_course(grade.course_name)


def main():

    # create a stevens Repository
    stevens = Repository(os.path.abspath('stevens_dir'))

    # add courses to students and instructor
    stevens.analysis_grades()

    # print student and instructors table
    stevens.show_students()

    stevens.show_instructors()


if __name__ == '__main__':
    main()
