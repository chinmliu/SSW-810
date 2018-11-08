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
from operator import itemgetter


class People(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def say(self):
        pass

    @abc.abstractmethod
    def courses_result(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def get_fields():
        pass


class Grade:
    def __init__(self, stu_id, course_name, score, instr_id):
        self.stu_id = stu_id
        self.score = score
        self.course_name = course_name
        self.instr_id = instr_id


class Student(People):
    def say(self):
        print('Hello!')

    def __init__(self, CWID, name, major):
        self.CWID = CWID
        self.name = name
        self.major = major
        self.courses = dict()

    def add_course(self, course_name, score):
        self.courses[course_name] = score

    def courses_result(self):
        left_courses = self.major.get_left_courses(self.get_pass_courses())
        left_elective_courses = [course for course in left_courses.keys()
                                 if left_courses[course] == "E"]
        left_required_courses = [course for course in left_courses.keys()
                                 if left_courses[course] == "R"]
        return [self.CWID, self.name, self.major.name,
                (lambda: list(self.get_pass_courses().keys()) if len(self.get_pass_courses().keys()) > 0 else None)(),
                left_required_courses,
                (lambda: None
                    if len(left_elective_courses) < len([course for course in self.major.courses.keys()
                        if self.major.courses[course] == "E"]) else left_elective_courses)()]

    def get_pass_courses(self):
        pass_courses_names = [courses_name for courses_name in self.courses.keys() if self.courses[courses_name] != "F"]
        pass_courses = dict()
        for pass_courses_name in pass_courses_names:
            pass_courses[pass_courses_name] = self.courses[pass_courses_name]
        return pass_courses

    @staticmethod
    def get_fields():
        return ["CWID", "Name", "Major", "Completed Course", "Remaining Required", "Remaining Electives"]


class Instructor(People):
    def say(self):
        print('Hello!')

    def __init__(self, CWID, name, dept):
        self.CWID = CWID
        self.name = name
        self.dept = dept
        self.courses = defaultdict(int)

    def add_course(self, course_name):
        self.courses[course_name] += 1

    def courses_result(self):
        courses_result_list = []
        for course_name in self.courses.keys():
            courses_result_list.append([self.CWID, self.name, self.dept, course_name, self.courses[course_name]])
        return courses_result_list

    @staticmethod
    def get_fields():
        return ["CWID", "Name", "Dept", "Course", "Students"]


class Utils:
    @staticmethod
    def read_lines(path):
        lines = []
        try:
            file = open(path)
        except FileNotFoundError:
            raise FileNotFoundError(f'warning: file({path}) not found')
        with file:
            for line in file:
                attr = line.strip().split(f'\t')
                if len(attr) != 0 or attr is not None:
                    lines.append(attr)
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
        self.majors = dict()
        self.majors_path = os.path.join(init_dir, 'majors.txt')
        self.read_majors(self.majors_path)

    def read_student(self, path):
        for CWID, name, major_name in Utils.read_lines(path):
            student = Student(CWID, name, self.majors[major_name])
            self.students[student.CWID] = student
        return self.students

    def read_instructors(self, path):
        for cwid, name, dept in Utils.read_lines(path):
            instructor = Instructor(cwid, name, dept)
            self.instructors[instructor.CWID] = instructor
        return self.instructors

    def read_grades(self, path):
        for s_CWID, course_name, score, ins_id in Utils.read_lines(path):
            grade = Grade(s_CWID, course_name, score, ins_id)
            self.grades[grade.stu_id, grade.course_name] = grade
        return self.grades

    def show_students(self):
        student_summary_table = PrettyTable()
        student_summary_table.field_names = Student.get_fields()
        sorted_students = sorted(self.students.items(), key=itemgetter(0))
        for item in sorted_students:
            student_summary_table.add_row(item[1].courses_result())
        print(student_summary_table.get_string())

    def show_instructors(self):
        instructor_summary_table = PrettyTable()
        instructor_summary_table.field_names = Instructor.get_fields()
        sorted_instructors = sorted(self.instructors.items(), key=itemgetter(0))
        for item in sorted_instructors:
            for data in item[1].courses_result():
                instructor_summary_table.add_row(data)
        print(instructor_summary_table.get_string())

    def analysis_grades(self):
        for grade in self.grades.values():
            self.students.get(grade.stu_id).add_course(grade.course_name, grade.score)
            self.instructors.get(grade.ins_id).add_course(grade.course_name)

    def read_majors(self, path):
        for major_name, course_type, course_name in Utils.read_lines(path):
            if major_name not in self.majors.keys():
                major = Major(major_name)
                self.majors[major_name] = major
            self.majors[major_name].courses[course_name] = course_type

    def show_majors(self):
        major_table = PrettyTable()
        major_table.field_names = Major.get_field_name()
        for major in self.majors.values():
            major_table.add_row(major.pt_show())
        print(major_table.get_string())


class Major:
    def __init__(self, name):
        self.name = name
        self.courses = dict()

    def add_course(self, course_name, type):
        self.courses[course_name] = type

    def get_left_courses(self, stu_courses):
        left_dict = dict()
        for course_name in self.courses.keys():
            if course_name not in stu_courses.keys():
                left_dict[course_name] = self.courses[course_name]
        return left_dict

    def pt_show(self):
        return [self.name, [course for course in self.courses.keys() if self.courses[course] is "R"],
                [course for course in self.courses.keys() if self.courses[course] is "E"]]

    @staticmethod
    def get_field_name():
        return ["DEPT", "Required", "Electives"]


def main():

    # create a stevens Repository
    stevens = Repository(os.path.abspath('stevens_dir'))

    # add courses to students and instructor
    stevens.analysis_grades()

    # print student and instructors table
    stevens.show_students()
    stevens.show_instructors()

    # print major table
    stevens.show_majors()


if __name__ == '__main__':
    main()
