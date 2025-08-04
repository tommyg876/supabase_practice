class Student:
    def __init__ (self, id, name):
        self.id = id
        self.name = name
        self.subjects = []
    
    def add_subject (self, subject):
        self.subjects.append(subject)
    
    def __str__ (self):
        subject_list = ", ".join(str(s) for s in self.subjects)
        return f"{self.name} has subjects: {subject_list}"

class Subject:
    def __init__ (self, name, school_mark, mark):
        self.name = name
        self.school_mark = school_mark
        self.exam_mark = mark
    
    def average(self):
        return (self.school_mark + self.exam_mark) / 2

    def __str__(self):
        return f"{self.name}: {self.average():.2f}"

student = Student(3, 'Tommy')
math = Subject('Math Advanced', 88, 92)
eng = Subject('English Standard', 75, 78)

student.add_subject(math)
student.add_subject(eng)

print(student)
