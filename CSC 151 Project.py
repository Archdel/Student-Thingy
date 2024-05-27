import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import re

class Student:
    def __init__(self, id: str, first_name: str,middle_name: str,last_name: str, lvl: str, gender: str, course_code: str) -> None:
        self.id = id
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.lvl = lvl
        self.gender = gender
        self.course_code = course_code
    
    def __str__(self) -> str:
        return f'id: {self.id}, first_name: {self.first_name}, middle_name:{self.middle_name}, last_name: {self.last_name}, level: {self.lvl}, gender: {self.gender}, course code: {self.course_code}'

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
                    if all(field in row for field in ['id', 'first_name', 'middle_name', 'last_name', 'lvl', 'gender', 'course_code']):
                        students.append(Student(row['id'], row['first_name'], row['middle_name'], row['last_name'], row['lvl'], row['gender'], row['course_code']))
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
        fieldnames = ["id", "first_name", "middle_name", "last_name", "lvl", "gender", "course_code"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for student in students:
            writer.writerow({"id": student.id, "first_name": student.first_name,"middle_name": student.middle_name, "last_name": student.last_name, "lvl": student.lvl, "gender": student.gender, "course_code": student.course_code})
    messagebox.showinfo("Success", "Students data saved successfully.")

def save_courses_to_csv(courses):
    with open('courses.csv', mode='w', newline='') as csvfile:
        fieldnames = ["course_code", "course_name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for course in courses:
            writer.writerow({"course_code": course.course_code, "course_name": course.course_name})
    messagebox.showinfo("Success", "Courses data saved successfully.")

def add_student(students, courses, id_number, first_name, middle_name, last_name, lvl, gender, course_code):
    if any(student.id == id_number for student in students):
        messagebox.showerror("Error", "Student with this ID already exists.")
        return

    if not re.match(r'^\d{4}-\d{4}$', id_number):
        messagebox.showerror("Error", "Invalid ID format. Please enter in the format XXXX-XXXX.")
        return

    if not first_name.replace(" ", "").isalpha():
        messagebox.showerror("Error", "Invalid name format. Please enter only alphabetic characters.")
        return
    
    if not middle_name.replace(" ", "").isalpha():
        messagebox.showerror("Error", "Invalid name format. Please enter only alphabetic characters.")
        return
    if not last_name.replace(" ", "").isalpha():
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

    student = Student(id_number, first_name, middle_name, last_name, lvl, gender, course_code)
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
        
        view_list = tk.Button(self, text="View Students", command=lambda: controller.show_frame(ViewStudents))
        view_list.pack()
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
        first_name_label = tk.Label(self, text="First Name: ")
        first_name_label.place(x=10, y=110)
        self.first_name_entry = tk.Entry(self, width=25)
        self.first_name_entry.place(x=80,y=110)
        middle_name_label = tk.Label(self, text="Middle Name: ")
        middle_name_label.place(x=210, y=110)
        self.middle_name_entry = tk.Entry(self, width=15)
        self.middle_name_entry.place(x=300,y=110)
        last_name_label = tk.Label(self, text="Last Name: ")
        last_name_label.place(x=410, y=110)
        self.last_name_entry = tk.Entry(self, width=15)
        self.last_name_entry.place(x=480,y=110)
        lvl_label = tk.Label(self, text="Year Level: ")
        lvl_label.place(x=10, y=140)
        self.lvl_entry = tk.Entry(self, width=5)
        self.lvl_entry.place(x=10, y=170)
        self.gender_var = tk.StringVar()
        self.gender_var.set("Male")
        male_radio = tk.Radiobutton(self, text="Male", variable=self.gender_var, value="M")
        male_radio.place(x=210, y=140)
        female_radio = tk.Radiobutton(self, text="Female", variable=self.gender_var, value="F")
        female_radio.place(x=210, y=170)
        id_label = tk.Label(self, text="Course Code: ")
        id_label.place(x=10, y=210)
        self.course_entry = tk.Entry(self, width=30)
        self.course_entry.place(x=10, y=230)
        
        add_button = tk.Button(self, text="Add", command=self.add_student)
        add_button.place(x=400, y=230)
        back_button = tk.Button(self, text="Back",command=lambda: controller.show_frame(ViewStudents))
        back_button.place(x=400, y=260)
        
    def add_student(self):
        id_number = self.id_entry.get()
        first_name = self.first_name_entry.get().upper().strip()
        middle_name = self.middle_name_entry.get().upper().strip()
        last_name = self.last_name_entry.get().upper().strip()
        lvl = self.lvl_entry.get()
        gender = self.gender_var.get()
        course_code = self.course_entry.get().upper().strip()
        
        add_student(students, courses, id_number, first_name, middle_name, last_name, lvl, gender, course_code)
        self.controller.frames[ViewStudents].refresh_treeview()

    

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
        
        delete_button = tk.Button(self, text="Delete", command=self.confirm_delete_student)
        delete_button.place(x=75, y=110)
        back_button = tk.Button(self, text="Back",command=lambda: controller.show_frame(ViewStudents))
        back_button.place(x=180, y=260)

    def confirm_delete_student(self):
        id_to_delete = self.id_entry.get()
        confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete student with ID {id_to_delete}?")
        if confirmation:
            delete_student(students, id_to_delete)
            self.controller.frames[ViewStudents].refresh_treeview()

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
        back_button = tk.Button(self, text="Back",command=lambda: controller.show_frame(ViewCourses))
        back_button.place(x=180, y=260)

    def add_course(self):
        course_code = self.code_entry.get().upper().strip()
        if any(course.course_code == course_code for course in courses):
            messagebox.showerror("Error", "Course with this Course Code already exists.")
            return
        course_name = self.course_entry.get().upper().strip()
        courses.append(Course(course_code, course_name))
        save_courses_to_csv(courses)
        self.controller.frames[ViewStudents].refresh_treeview()

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
        back_button = tk.Button(self, text="Back",command=lambda: controller.show_frame(ViewCourses))
        back_button.place(x=180, y=260)
        
        delete_button = tk.Button(self, text="Delete", command=self.confirm_delete_course)
        delete_button.place(x=110, y=80)

    def confirm_delete_course(self):
        course_code = self.code_entry.get().upper().strip()
        confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete course with code {course_code}?")
        if confirmation:
            delete_course(students, courses, course_code)
            self.controller.frames[ViewStudents].refresh_treeview()

class ViewStudents(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Student List", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_student) 
        self.search_entry = tk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack()
        back_button = tk.Button(self, text="Back",command=lambda: controller.show_frame(Front))
        back_button.pack()
        add_st = tk.Button(self, text="Edit Student", command=lambda: controller.show_frame(EditStudent))
        add_st.pack(side=tk.RIGHT, padx=5)
        delete_st = tk.Button(self, text="Delete Student", command=lambda: controller.show_frame(DeleteStudent))
        delete_st.pack(side=tk.RIGHT, padx=5, pady=10)
        add_st = tk.Button(self, text="Add Student", command=lambda: controller.show_frame(AddStudent))
        add_st.pack(side=tk.RIGHT, padx=5)
        self.tree = ttk.Treeview(self, columns=('ID', 'First Name', 'Middle Name', 'Last Name', 'Level', 'Gender', 'Course Code'), show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.heading('ID', text='ID')
        self.tree.heading('First Name', text='First Name')
        self.tree.heading('Middle Name', text='Middle Name')
        self.tree.heading('Last Name', text='Last Name')
        self.tree.heading('Level', text='Level')
        self.tree.heading('Gender', text='Gender')
        self.tree.heading('Course Code', text='Course Code')
        self.tree.column('ID', width=100)
        self.tree.column('First Name', width=100) 
        self.tree.column('Middle Name', width=100) 
        self.tree.column('Last Name', width=100)
        self.tree.column('Level', width=50)  
        self.tree.column('Gender', width=50) 
        self.tree.column('Course Code', width=100)  
        self.populate_treeview()

    def populate_treeview(self):
        sorted_students = sort_students_by_id(students)
        for student in sorted_students:
            self.tree.insert('', tk.END, values=(student.id, student.first_name, student.middle_name, student.last_name, student.lvl, student.gender, student.course_code if student.course_code else None))
            
    def refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        self.populate_treeview()

    def search_student(self, *args):
        search_query = self.search_var.get().lower()
        if search_query:
            self.tree.delete(*self.tree.get_children())
            for student in students:
                student_data = [str(student.id), student.first_name, student.middle_name, student.last_name, student.lvl, student.gender, student.course_code if student.course_code else None]
                if any(search_query in str(data).lower() for data in student_data):
                    self.tree.insert('', tk.END, values=student_data)
        else:
            self.refresh_treeview()
    
            
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
        search_button.place(x=310, y=50)
        self.first_name_var = tk.StringVar()
        self.middle_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.lvl_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.course_var = tk.StringVar()
        first_name_label = tk.Label(self, text="First Name:")
        first_name_label.place(x=10, y=110)
        self.first_name_entry = tk.Entry(self, width=25, textvariable=self.first_name_var)
        self.first_name_entry.place(x=80,y=110)
        middle_name_label = tk.Label(self, text="Middle Name:")
        middle_name_label.place(x=210, y=110)
        self.middle_name_entry = tk.Entry(self, width=15, textvariable=self.middle_name_var)
        self.middle_name_entry.place(x=300,y=110)
        last_name_label = tk.Label(self, text="Last Name:")
        last_name_label.place(x=410, y=110)
        self.last_name_entry = tk.Entry(self, width=15, textvariable=self.last_name_var)
        self.last_name_entry.place(x=500, y=110)
        lvl_label = tk.Label(self, text="Year Level:")
        lvl_label.place(x=10, y=140)
        self.lvl_entry = tk.Entry(self, width=5, textvariable=self.lvl_var)
        self.lvl_entry.place(x=80, y=140)
        gender_label = tk.Label(self, text="Gender:")
        gender_label.place(x=10, y=170)
        self.gender_combo = ttk.Combobox(self, width=27, textvariable=self.gender_var, state="readonly")
        self.gender_combo['values'] = ('M', 'F')
        self.gender_combo.place(x=80, y=170)
        course_label = tk.Label(self, text="Course Code:")
        course_label.place(x=10, y=200)
        self.course_entry = tk.Entry(self, width=30, textvariable=self.course_var)
        self.course_entry.place(x=10, y=230)
        save_button = tk.Button(self, text="Save", command=self.save_student)
        save_button.place(x=400, y=230)
        cancel_button = tk.Button(self, text="Cancel", command=lambda: controller.show_frame(ViewStudents))
        cancel_button.place(x=400, y=260)

    def search_student(self):
        student_id = self.id_entry.get().upper().strip()
        found_student = None
        for student in students:
            if student.id == student_id:
                found_student = student
                break
        if found_student:
            self.first_name_var.set(found_student.first_name)
            self.middle_name_var.set(found_student.middle_name)
            self.last_name_var.set(found_student.last_name)
            self.lvl_var.set(found_student.lvl)
            self.gender_var.set(found_student.gender)
            self.course_var.set(found_student.course_code)
        else:
            messagebox.showinfo("Error", "Student not found.")
    
    def course_exists(self, course_code: str) -> bool:
        with open('courses.csv', 'r') as file:
            reader = csv.DictReader(file)

            for course in reader:
                if course['course_code'] == course_code:
                    return True
            
            return False
    
    def save_student(self):
        student_id = self.id_entry.get()
        first_name = self.first_name_entry.get().upper().strip()
        middle_name = self.middle_name_entry.get().upper().strip()
        last_name = self.last_name_entry.get().upper().strip()
        lvl = self.lvl_entry.get()
        gender = self.gender_var.get().upper().strip()
        course_code = self.course_entry.get().upper().strip()
        for student in students:
            if self.course_exists(course_code):
                if student.id == student_id:
                    student.first_name = first_name
                    student.middle_name = middle_name
                    student.last_name = last_name
                    student.lvl = lvl
                    student.gender = gender
                    student.course_code = course_code
                    save_students_to_csv(students)
                    self.controller.frames[ViewStudents].refresh_treeview()
                    messagebox.showinfo("Success", "Student information updated successfully.")
                    self.controller.show_frame(Front)
                    return
                return messagebox.showinfo("Error", "Student not found.")
            return messagebox.showinfo("Error", "Course Code not found.")

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

        self.ccode_var = tk.StringVar()
        ccode_label = tk.Label(self, text="Course Name:")
        ccode_label.place(x=400, y=80)
        self.ccode_entry = tk.Entry(self, width=30, textvariable=self.ccode_var)
        self.ccode_entry.place(x=440, y=80)
        
        self.name_var = tk.StringVar()
        name_label = tk.Label(self, text="Course Name:")
        name_label.place(x=10, y=80)
        self.name_entry = tk.Entry(self, width=30, textvariable=self.name_var)
        self.name_entry.place(x=150, y=80)
        
        save_button = tk.Button(self, text="Save", command=self.save_course)
        save_button.place(x=150, y=110)
        
        cancel_button = tk.Button(self, text="Cancel", command=lambda: controller.show_frame(ViewCourses))
        cancel_button.place(x=230, y=110)

    def search_course(self):
        course_code = self.code_entry.get().upper().strip()
        found_course = None
        for course in courses:
            if course.course_code == course_code:
                found_course = course
                break
        if found_course:
            self.name_var.set(found_course.course_name)
            self.ccode_var.set(found_course.course_code)
        else:
            messagebox.showinfo("Error", "Course not found.")

    def save_course(self):
        course_code = self.code_entry.get().upper().strip()
        course_name = self.name_entry.get().upper().strip()
        for course in courses:
            if course.course_code == course_code:
                course.course_code = self.ccode_entry.get().upper().strip()
                course.course_name = course_name
                save_courses_to_csv(courses)
                self.controller.frames[ViewCourses].refresh_treeview()
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
        self.search_var.trace("w", self.search_course)  
        self.search_entry = tk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack()
        back_button = tk.Button(self, text="Back",command=lambda: controller.show_frame(Front))
        back_button.pack()
        self.tree = ttk.Treeview(self, columns=('Course Code', 'Course Name'), show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.heading('Course Code', text='Course Code')
        self.tree.heading('Course Name', text='Course Name')
        self.tree.column('Course Code', width=100)  
        self.tree.column('Course Name', width=200)  
        
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.tree.configure(yscroll=scrollbar.set)

        add_co = tk.Button(self, text="Add Course", command=lambda: controller.show_frame(AddCourse))
        add_co.pack(side=tk.LEFT, padx=5)
        delete_co = tk.Button(self, text="Delete Course", command=lambda: controller.show_frame(DeleteCourse))
        delete_co.pack(side=tk.LEFT, padx=5)
        add_st = tk.Button(self, text="Edit Course", command=lambda: controller.show_frame(EditCourse))
        add_st.pack(side=tk.LEFT, padx=5)

        self.populate_treeview()

    def search_course(self, *args):
        search_query = self.search_var.get().lower()
        if search_query:
            self.tree.delete(*self.tree.get_children())
            for course in courses:
                course_data = [course.course_code, course.course_name]
                if any(search_query in str(data).lower() for data in course_data):
                    self.tree.insert('', tk.END, values=course_data)
        else:
            self.refresh_treeview()

    def populate_treeview(self):
        for course in courses:
            self.tree.insert('', tk.END, values=(course.course_code, course.course_name))

    def refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        self.populate_treeview()

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
        
        for F in (Front, AddStudent, DeleteStudent, AddCourse, DeleteCourse, ViewStudents, EditStudent, EditCourse, ViewCourses):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(Front)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


if __name__ == "__main__":
    app = SampleApp()
    app.state('zoomed')
    app.title("Page Navigation Example")
    app.mainloop()
