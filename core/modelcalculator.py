from database import Student, Subject  

class ATARCalculator:
    def __init__(self, student: Student):
        self.student = student

    def predict(self):
        total = 0
        for subject in self.student.subjects:
            total += subject.average()
        
        total_subjects = len(self.student.subjects)
        avg = total / total_subjects
        return round(avg * total_subjects) / total_subjects



student = Student(3, 'Tommy')
math = Subject('Math Advanced', 88, 92)
english = Subject('English Standard', 75, 79)

student.add_subject(math)
student.add_subject(english)

calc = ATARCalculator(student)
prediction = calc.predict()
print(f"Predicted ATAR: {prediction}")
