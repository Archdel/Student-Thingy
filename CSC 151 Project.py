import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import re

class Student:
    def __init__(self, id: str, name: str, lvl: str, gender: str, course_code: str) -> None:
        self.id = id
        self.name = name
        self.lvl = lvl
        self.gender = gender
        self.course_code = course_code
    
    def __str__(self) -> str:
        return f'id: {self.id}, name: {self.name}, level: {self.lvl}, gender: {self.gender}, course code: {self.course_code}'

class Course:
    def __init__(self, course_code: str, course_name: str) -> None:
        self.course_code = course_code
        self.course_name = course_name

def load_students_from_csv():
    students = []
    try:
        if os.path.isfile('students.csv') and os.path.getsize('students.csv') > 0:
            with open('students.csv', mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if all(field in row for field in ['id', 'name', 'lvl', 'gender', 'course_code']):
                        students.append(Student(row['id'], row['name'], row['lvl'], row['gender'], row['course_code']))
                    else:
                        print("Error: Missing or incomplete data for a student in students.csv")
    except FileNotFoundError:
        pass
    return students

def load_courses_from_csv():
    courses = []
    try:
        if os.path.isfile('courses.csv') and os.path.getsize('courses.csv') > 0:
            with open('courses.csv', mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 'course_code' in row and 'course_name' in row:
                        courses.append(Course(row['course_code'], row['course_name']))
                    else:
                        print("Error: Missing data in courses.csv")
    except FileNotFoundError:
        pass
    return courses

def save_students_to_csv(students):
    with open('students.csv', mode='w', newline='') as csvfile:
        fieldnames = ["id", "name", "lvl", "gender", "course_code"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for student in students:
            writer.writerow({"id": student.id, "name": student.name, "lvl": student.lvl, "gender": student.gender, "course_code": student.course_code})
    messagebox.showinfo("Success", "Students data saved successfully.")

def save_courses_to_csv(courses):
    with open('courses.csv', mode='w', newline='') as csvfile:
        fieldnames = ["course_code", "course_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for course in courses:
            writer.writerow({"course_code": course.course_code, "course_name": course.course_name})
    messagebox.showinfo("Success", "Courses data saved successfully.")

def add_student(students, courses, id_number, name, lvl, gender, course_code):
    if any(student.id == id_number for student in students):
        messagebox.showerror("Error", "Student with this ID already exists.")
        return

    if not re.match(r'^\d{4}-\d{4}$', id_number):
        messagebox.showerror("Error", "Invalid ID format. Please enter in the format XXXX-XXXX.")
        return

    if not name.replace(" ", "").isalpha():
        messagebox.showerror("Error", "Invalid name format. Please enter only alphabetic characters.")
        return

    if not lvl.isdigit() or not 1 <= int(lvl) <= 6:
        messagebox.showerror("Error", "Invalid year level. Please enter a single digit whole number between 1 and 6.")
        return

    if gender not in ('M', 'F'):
        messagebox.showerror("Error", "Invalid gender. Please enter 'M' for Male or 'F' for Female.")
        return

    if not re.match(r'^[A-Z0-9-]{4,15}$', course_code):
        messagebox.showerror("Error", "Invalid course code format. Please enter 4-15 alphanumeric characters.")
        return

    course_exist = any(course.course_code.lower() == course_code.lower() for course in courses)

    if not course_exist:
        messagebox.showerror("Error", "Course Code does not exist")
        return

    student = Student(id_number, name, lvl, gender, course_code)
    students.append(student)

    save_students_to_csv(students)
    save_courses_to_csv(courses)

def delete_student(students, id_to_delete):
    for student in students:
        if student.id == id_to_delete:
            students.remove(student)
            save_students_to_csv(students) 
            messagebox.showinfo("Success", "Student deleted successfully.")
            return
    messagebox.showerror("Error", "Student not found.")

def delete_course(students, courses, course_code):
    for course in courses:
        if course.course_code.lower() == course_code.lower():
            courses.remove(course)
            break
    else:
        messagebox.showerror("Error", "Course not found.")
        return

    for student in students:
        if student.course_code.lower() == course_code.lower():
            student.course_code = ""

    save_students_to_csv(students)
    save_courses_to_csv(courses)

    messagebox.showinfo("Success", "Course deleted successfully.")

def sort_students_by_id(students):
    return sorted(students, key=lambda student: student.id)

class Front(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="What would you like to do?", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        
        add_st = tk.Button(self, text="Add Student", command=lambda: controller.show_frame(AddStudent))
        add_st.pack()
        delete_st = tk.Button(self, text="Delete Student", command=lambda: controller.show_frame(DeleteStudent))
        delete_st.pack()
        add_st = tk.Button(self, text="Edit Student", command=lambda: controller.show_frame(EditStudent))
        add_st.pack()
        add_co = tk.Button(self, text="Add Course", command=lambda: controller.show_frame(AddCourse))
        add_co.pack()
        delete_co = tk.Button(self, text="Delete Course", command=lambda: controller.show_frame(DeleteCourse))
        delete_co.pack()
        view_list = tk.Button(self, text="View List", command=lambda: controller.show_frame(ViewList))
        view_list.pack()
        add_st = tk.Button(self, text="Edit Course", command=lambda: controller.show_frame(EditCourse))
        add_st.pack()
        add_st = tk.Button(self, text="View Courses", command=lambda: controller.show_frame(ViewCourses))
        add_st.pack()

class AddStudent(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Please fill out the information", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        id_label = tk.Label(self, text="ID Number: ")
        id_label.place(x=10, y=50)
        self.id_entry = tk.Entry(self, width=30)
        self.id_entry.place(x=10,y=80)
        name_label = tk.Label(self, text="Name: ")
        name_label.place(x=210, y=50)
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.place(x=210,y=80)
        lvl_label = tk.Label(self, text="Year Level: ")
        lvl_label.place(x=10, y=110)
        self.lvl_entry = tk.Entry(self, width=5)
        self.lvl_entry.place(x=10, y=140)
        self.gender_var = tk.StringVar()
        self.gender_var.set("Male")
        male_radio = tk.Radiobutton(self, text="Male", variable=self.gender_var, value="M")
        male_radio.place(x=210, y=110)
        female_radio = tk.Radiobutton(self, text="Female", variable=self.gender_var, value="F")
        female_radio.place(x=210, y=140)
        id_label = tk.Label(self, text="Course Code: ")
        id_label.place(x=10, y=170)
        self.course_entry = tk.Entry(self, width=30)
        self.course_entry.place(x=10, y=200)
        
        add_button = tk.Button(self, text="Add", command=self.add_student)
        add_button.place(x=180, y=230)

    def add_student(self):
        id_number = self.id_entry.get()
        name = self.name_entry.get()
        lvl = self.lvl_entry.get()
        gender = self.gender_var.get()
        course_code = self.course_entry.get()
        
        add_student(students, courses, id_number, name, lvl, gender, course_code)

class DeleteStudent(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Please fill out the information", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        id_label = tk.Label(self, text="ID Number:")
        id_label.place(x=10, y=50)
        self.id_entry = tk.Entry(self, width=30)
        self.id_entry.place(x=10, y=80)
        
        delete_button = tk.Button(self, text="Delete", command=self.delete_student)
        delete_button.place(x=75, y=110)

    def delete_student(self):
        id_to_delete = self.id_entry.get()
        delete_student(students, id_to_delete)

class AddCourse(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Please fill out the information", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        label = tk.Label(self, text="Course Code:")
        label.place(x=10, y=50)
        self.code_entry = tk.Entry(self, width=30)
        self.code_entry.place(x=110, y=50)
        label = tk.Label(self, text="Course Name:")
        label.place(x=10, y=80)
        self.course_entry = tk.Entry(self, width=30)
        self.course_entry.place(x=110, y=80)
        
        add_button = tk.Button(self, text="Add", command=self.add_course)
        add_button.place(x=110, y=110)

    def add_course(self):
        course_code = self.code_entry.get()
        course_name = self.course_entry.get()
        courses.append(Course(course_code, course_name))
        save_courses_to_csv(courses)

class DeleteCourse(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Please fill out the information", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        label = tk.Label(self, text="Course Code:")
        label.place(x=10, y=50)
        self.code_entry = tk.Entry(self, width=30)
        self.code_entry.place(x=110, y=50)
        
        delete_button = tk.Button(self, text="Delete", command=self.delete_course)
        delete_button.place(x=110, y=80)

    def delete_course(self):
        course_code = self.code_entry.get()
        delete_course(students, courses, course_code)

class ViewList(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Student List", font=("Arial", 18))
        label.pack(pady=10, padx=10)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack()
        search_button = tk.Button(self, text="Search", command=self.search_student)
        search_button.pack()
        self.tree = ttk.Treeview(self, columns=('ID', 'Name', 'Level', 'Gender', 'Course Code'))
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Level', text='Level')
        self.tree.heading('Gender', text='Gender')
        self.tree.heading('Course Code', text='Course Code')
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.tree.configure(yscroll=scrollbar.set)
        self.populate_treeview()

    def populate_treeview(self):
        sorted_students = sort_students_by_id(students)
        for student in sorted_students:
            self.tree.insert('', tk.END, values=(student.id, student.name, student.lvl, student.gender, student.course_code))

    def search_student(self):
        search_id = self.search_var.get()
        if search_id:
            self.tree.delete(*self.tree.get_children())  # Clear existing items
            found_student = None
            for student in students:
                if student.id == search_id:
                    found_student = student
                    self.tree.insert('', tk.END, values=(found_student.id, found_student.name, found_student.lvl, found_student.gender, found_student.course_code))
                    break
            if not found_student:
                messagebox.showinfo("Info", "Student not found.")
        else:
            messagebox.showinfo("Info", "Please enter a student ID to search.")

            
class EditStudent(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Edit Student Information", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        id_label = tk.Label(self, text="Enter ID Number:")
        id_label.place(x=10, y=50)
        self.id_entry = tk.Entry(self, width=30)
        self.id_entry.place(x=150, y=50)
        search_button = tk.Button(self, text="Search", command=self.search_student)
        search_button.place(x=300, y=50)
        self.name_var = tk.StringVar()
        self.lvl_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.course_var = tk.StringVar()
        name_label = tk.Label(self, text="Name:")
        name_label.place(x=10, y=100)
        self.name_entry = tk.Entry(self, width=30, textvariable=self.name_var)
        self.name_entry.place(x=150, y=100)
        lvl_label = tk.Label(self, text="Year Level:")
        lvl_label.place(x=10, y=130)
        self.lvl_entry = tk.Entry(self, width=5, textvariable=self.lvl_var)
        self.lvl_entry.place(x=150, y=130)
        gender_label = tk.Label(self, text="Gender:")
        gender_label.place(x=10, y=160)
        self.gender_combo = ttk.Combobox(self, width=27, textvariable=self.gender_var, state="readonly")
        self.gender_combo['values'] = ('M', 'F')
        self.gender_combo.place(x=150, y=160)
        course_label = tk.Label(self, text="Course Code:")
        course_label.place(x=10, y=190)
        self.course_entry = tk.Entry(self, width=30, textvariable=self.course_var)
        self.course_entry.place(x=150, y=190)
        save_button = tk.Button(self, text="Save", command=self.save_student)
        save_button.place(x=150, y=230)
        cancel_button = tk.Button(self, text="Cancel", command=lambda: controller.show_frame(Front))
        cancel_button.place(x=230, y=230)

    def search_student(self):
        student_id = self.id_entry.get()
        found_student = None
        for student in students:
            if student.id == student_id:
                found_student = student
                break
        if found_student:
            self.name_var.set(found_student.name)
            self.lvl_var.set(found_student.lvl)
            self.gender_var.set(found_student.gender)
            self.course_var.set(found_student.course_code)
        else:
            messagebox.showinfo("Error", "Student not found.")

    def save_student(self):
        student_id = self.id_entry.get()
        name = self.name_entry.get()
        lvl = self.lvl_entry.get()
        gender = self.gender_var.get()
        course_code = self.course_entry.get()
        for student in students:
            if student.id == student_id:
                student.name = name
                student.lvl = lvl
                student.gender = gender
                student.course_code = course_code
                save_students_to_csv(students)
                messagebox.showinfo("Success", "Student information updated successfully.")
                self.controller.show_frame(Front)
                return
        messagebox.showinfo("Error", "Student not found.")

class EditCourse(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Edit Course Information", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        
        code_label = tk.Label(self, text="Enter Course Code:")
        code_label.place(x=10, y=50)
        self.code_entry = tk.Entry(self, width=30)
        self.code_entry.place(x=150, y=50)
        
        search_button = tk.Button(self, text="Search", command=self.search_course)
        search_button.place(x=300, y=50)

        self.name_var = tk.StringVar()
        name_label = tk.Label(self, text="Course Name:")
        name_label.place(x=10, y=80)
        self.name_entry = tk.Entry(self, width=30, textvariable=self.name_var)
        self.name_entry.place(x=150, y=80)
        
        save_button = tk.Button(self, text="Save", command=self.save_course)
        save_button.place(x=150, y=110)
        
        cancel_button = tk.Button(self, text="Cancel", command=lambda: controller.show_frame(Front))
        cancel_button.place(x=230, y=110)

    def search_course(self):
        course_code = self.code_entry.get()
        found_course = None
        for course in courses:
            if course.course_code == course_code:
                found_course = course
                break
        if found_course:
            self.name_var.set(found_course.course_name)
        else:
            messagebox.showinfo("Error", "Course not found.")

    def save_course(self):
        course_code = self.code_entry.get()
        course_name = self.name_entry.get()
        for course in courses:
            if course.course_code == course_code:
                course.course_name = course_name
                save_courses_to_csv(courses)
                messagebox.showinfo("Success", "Course information updated successfully.")
                self.controller.show_frame(Front)
                return
        messagebox.showinfo("Error", "Course not found.")

class ViewCourses(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Course List", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack()
        search_button = tk.Button(self, text="Search", command=self.search_course)
        search_button.pack()
        
        self.tree = ttk.Treeview(self, columns=('Course Code', 'Course Name'))
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.heading('Course Code', text='Course Code')
        self.tree.heading('Course Name', text='Course Name')
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.tree.configure(yscroll=scrollbar.set)

        self.populate_treeview()

    def search_course(self):
        search_code = self.search_var.get()
        if search_code:
            self.tree.delete(*self.tree.get_children())  # Clear existing items
            found_course = None
            for course in courses:
                if course.course_code == search_code:
                    found_course = course
                    self.tree.insert('', tk.END, values=(found_course.course_code, found_course.course_name))
                    break
            if not found_course:
                messagebox.showinfo("Info", "Course not found.")
        else:
            messagebox.showinfo("Info", "Please enter a course code to search.")

    def populate_treeview(self):
        for course in courses:
            self.tree.insert('', tk.END, values=(course.course_code, course.course_name))

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}

        global students
        global courses
        students = load_students_from_csv()
        courses = load_courses_from_csv()
        
        for F in (Front, AddStudent, DeleteStudent, AddCourse, DeleteCourse, ViewList, EditStudent, EditCourse, ViewCourses):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(Front)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


if __name__ == "__main__":
    app = SampleApp()
    app.geometry("400x300")
    app.title("Page Navigation Example")
    app.mainloop()
