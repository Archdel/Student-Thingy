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
    messagebox.showinfo("Success", "Student added successfully.")

def delete_student(students, id_to_delete):
    for student in students:
        if student.id == id_to_delete:
            students.remove(student)
            save_students_to_csv(students) 
            return True  
    return False  

def delete_course(students, courses, course_code):
    course_exists = False 
    for course in courses:
        if course.course_code.lower() == course_code.lower():
            courses.remove(course)
            course_exists = True
            break
    
    if not course_exists:
        messagebox.showerror("Error", "Course not found.")
        return False  


    for student in students:
        if student.course_code.lower() == course_code.lower():
            student.course_code = ""

    save_students_to_csv(students)
    save_courses_to_csv(courses)
    return True  


def sort_students_by_id(students):
    return sorted(students, key=lambda student: student.id)

class Front(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="What would you like to do?", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        
        view_students = tk.Button(self, text="View Students", command=lambda: controller.show_frame(ViewStudents))
        view_students.pack()
        view_courses = tk.Button(self, text="View Courses", command=lambda: controller.show_frame(ViewCourses))
        view_courses.pack()

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
        add_st = tk.Button(self, text="Edit Student", command=self.edit_student)
        add_st.pack(side=tk.RIGHT, padx=5)
        delete_st = tk.Button(self, text="Delete Student", command=self.delete_student)
        delete_st.pack(side=tk.RIGHT, padx=5, pady=10)
        add_st = tk.Button(self, text="Add Student", command=self.add_student)
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
    
    def add_student(self):
        add_window = tk.Toplevel(self)
        add_window.title("Add Student")

        tk.Label(add_window, text="Add Student", font=("Arial", 18)).pack(pady=10, padx=10)

        tk.Label(add_window, text="ID Number:").pack()
        id_entry = tk.Entry(add_window, width=30)
        id_entry.pack()

        tk.Label(add_window, text="First Name:").pack()
        first_name_entry = tk.Entry(add_window, width=30)
        first_name_entry.pack()


        tk.Label(add_window, text="Middle Name:").pack()
        middle_name_entry = tk.Entry(add_window, width=30)
        middle_name_entry.pack()

        tk.Label(add_window, text="Last Name:").pack()
        last_name_entry = tk.Entry(add_window, width=30)
        last_name_entry.pack()

        tk.Label(add_window, text="Gender:").pack()
        gender_var = tk.StringVar(add_window)
        gender_var.set("M") 
        gender_dropdown = tk.OptionMenu(add_window, gender_var, "M", "F")
        gender_dropdown.pack()

        tk.Label(add_window, text="Year Level:").pack()
        lvl_var = tk.StringVar(add_window)
        lvl_var.set("1") 
        lvl_dropdown = tk.OptionMenu(add_window, lvl_var, "1", "2", "3", "4", "5", "6")
        lvl_dropdown.pack()

        tk.Label(add_window, text="Course Code:").pack()
        course_entry = tk.Entry(add_window, width=30)
        course_entry.pack()

        def save_student():
            student_id = id_entry.get().strip().upper()
            first_name = first_name_entry.get().strip().upper()
            middle_name = middle_name_entry.get().strip().upper()
            last_name = last_name_entry.get().strip().upper()
            gender = gender_var.get().strip().upper()
            lvl = lvl_var.get().strip()
            course_code = course_entry.get().strip().upper()

            if not (student_id and first_name and last_name and gender and lvl and course_code):
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            add_student(students, courses, student_id, first_name, middle_name, last_name, lvl, gender, course_code)
            self.refresh_treeview()
            add_window.destroy()

        save_button = tk.Button(add_window, text="Save Student", command=save_student)
        save_button.pack(pady=10)


        
    def delete_student(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student?")
        if confirm:
            student_id = self.tree.item(selected_item)['values'][0] 
            success = delete_student(students, student_id) 
            if success:
                self.refresh_treeview()
                messagebox.showinfo("Success", "Student deleted successfully.")
            else:
                messagebox.showerror("Error", "Student not found.")

    def edit_student(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to edit.")
            return

        student_id = self.tree.item(selected_item)['values'][0]

        for student in students:
            if student.id == student_id:
                edit_window = tk.Toplevel(self)
                edit_window.title("Edit Student")

                tk.Label(edit_window, text="Edit Student", font=("Arial", 18)).pack(pady=10, padx=10)

                tk.Label(edit_window, text="ID Number:").pack()
                id_entry = tk.Entry(edit_window, width=30)
                id_entry.insert(0, student.id) 
                id_entry.pack()

                tk.Label(edit_window, text="First Name:").pack()
                first_name_entry = tk.Entry(edit_window, width=30)
                first_name_entry.insert(0, student.first_name) 
                first_name_entry.pack()

                tk.Label(edit_window, text="Middle Name:").pack()
                middle_name_entry = tk.Entry(edit_window, width=30)
                middle_name_entry.insert(0, student.middle_name)
                middle_name_entry.pack()

                tk.Label(edit_window, text="Last Name:").pack()
                last_name_entry = tk.Entry(edit_window, width=30)
                last_name_entry.insert(0, student.last_name)
                last_name_entry.pack()

                tk.Label(edit_window, text="Year Level:").pack()
                lvl_var = tk.StringVar(edit_window)
                lvl_var.set(student.lvl) 
                lvl_dropdown = tk.OptionMenu(edit_window, lvl_var, "1", "2", "3", "4", "5", "6")
                lvl_dropdown.pack()

                tk.Label(edit_window, text="Gender:").pack()
                gender_var = tk.StringVar(edit_window)
                gender_var.set(student.gender) 
                gender_dropdown = tk.OptionMenu(edit_window, gender_var, "M", "F")
                gender_dropdown.pack()

                tk.Label(edit_window, text="Course Code:").pack()
                course_entry = tk.Entry(edit_window, width=30)
                course_entry.insert(0, student.course_code) 
                course_entry.pack()

                def save_changes():
                    new_id = id_entry.get().strip().upper()
                    new_first_name = first_name_entry.get().strip().upper()
                    new_middle_name = middle_name_entry.get().strip().upper()
                    new_last_name = last_name_entry.get().strip().upper()
                    new_lvl = lvl_var.get().strip()
                    new_gender = gender_var.get().strip().upper()
                    new_course_code = course_entry.get().strip().upper()

                    if new_id != student.id and any(s.id == new_id for s in students):
                        messagebox.showerror("Error", "Student with this ID already exists.")
                        return

                    student.id = new_id
                    student.first_name = new_first_name
                    student.middle_name = new_middle_name
                    student.last_name = new_last_name
                    student.lvl = new_lvl
                    student.gender = new_gender
                    student.course_code = new_course_code

                    save_students_to_csv(students)
                    self.refresh_treeview()  
                    messagebox.showinfo("Success", "Changes saved successfully.")
                    edit_window.destroy()  

                save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
                save_button.pack(pady=10)
                break  
                

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

        add_co = tk.Button(self, text="Add Course", command=self.add_course)
        add_co.pack(side=tk.LEFT, padx=5)
        delete_co = tk.Button(self, text="Delete Course", command=self.delete_course)
        delete_co.pack(side=tk.LEFT, padx=5)
        add_st = tk.Button(self, text="Edit Course", command=self.edit_course)
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
    
    def add_course(self):
        add_window = tk.Toplevel(self)
        add_window.title("Add Course")

        tk.Label(add_window, text="Add Course", font=("Arial", 18)).pack(pady=10, padx=10)

        tk.Label(add_window, text="Course Code:").pack()
        code_entry = tk.Entry(add_window, width=30)
        code_entry.pack()

        tk.Label(add_window, text="Course Name:").pack()
        name_entry = tk.Entry(add_window, width=30)
        name_entry.pack()

        def save_course():
            course_code = code_entry.get().strip().upper()
            course_name = name_entry.get().strip().upper()

            if any(course.course_code == course_code for course in courses):
                messagebox.showerror("Error", "Course with this Course Code already exists.")
                return

            courses.append(Course(course_code, course_name))
            save_courses_to_csv(courses)
            self.refresh_treeview() 
            messagebox.showinfo("Success", "Course added successfully.")
            add_window.destroy()

        save_button = tk.Button(add_window, text="Save", command=save_course)
        save_button.pack(pady=10)

    def delete_course(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this course?")
        if confirm:
            course_code = self.tree.item(selected_item)['values'][0] 
            success = delete_course(students, courses, course_code)  
            if success:
                self.refresh_treeview()  
                messagebox.showinfo("Success", "Course deleted successfully.")
            else:
                messagebox.showerror("Error", "Course not found.")

    def edit_course(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to edit.")
            return

        old_course_code = self.tree.item(selected_item)['values'][0] 
        old_course_name = self.tree.item(selected_item)['values'][1]
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Course")

        tk.Label(edit_window, text="Edit Course", font=("Arial", 18)).pack(pady=10, padx=10)

        tk.Label(edit_window, text="Course Code:").pack()
        code_entry = tk.Entry(edit_window, width=30)
        code_entry.insert(tk.END, old_course_code) 
        code_entry.pack()

        tk.Label(edit_window, text="Course Name:").pack()
        name_entry = tk.Entry(edit_window, width=30)
        name_entry.insert(tk.END, old_course_name)
        name_entry.pack()

        def save_changes():
            new_course_code = code_entry.get().strip().upper()
            new_course_name = name_entry.get().strip().upper()

            for course in courses:
                if course.course_code == old_course_code:
                    course.course_code = new_course_code
                    course.course_name = new_course_name

                    for student in students:
                        if student.course_code == old_course_code:
                            student.course_code = new_course_code

                    save_courses_to_csv(courses)
                    save_students_to_csv(students)
                    self.refresh_treeview() 
                    messagebox.showinfo("Success", "Course information updated successfully.")
                    edit_window.destroy() 
                    return

            messagebox.showinfo("Error", "Course not found.")

        save_button = tk.Button(edit_window, text="Save", command=save_changes)
        save_button.pack(pady=10)


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
        
        for F in (Front, ViewStudents, ViewCourses):
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
