import tkinter as tk
from tkinter import ttk
import mysql.connector
import tkinter.messagebox as messagebox
import re

GENDER_VALUES = {
    "Male": "M",
    "Female": "F",
    "Other": "O"
}


class Student:
    def __init__(self, id, first_name, middle_name, last_name, lvl, gender, course_code):
        self.id = id
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.lvl = lvl
        self.gender = gender
        self.course_code = course_code
    
    def __str__(self):
        return f'ID: {self.id}, Name: {self.first_name} {self.middle_name} {self.last_name}, Level: {self.lvl}, Gender: {self.gender}, Course Code: {self.course_code}'

    def __init__(self, id, first_name, middle_name, last_name, lvl, gender, course_code):
        if not re.match(r'^20\d{2}-\d{4}$', id):
            raise ValueError("Invalid ID format. Please use the format '20XX-XXXX'.")
        self.id = id

        if not first_name or not first_name.isalpha():
            raise ValueError("First name must be a non-empty string containing only alphabetic characters.")
        self.first_name = first_name

        if not middle_name or not middle_name.isalpha():
            raise ValueError("Middle name must be a non-empty string containing only alphabetic characters.")
        self.middle_name = middle_name

        if not last_name or not last_name.isalpha():
            raise ValueError("Last name must be a non-empty string containing only alphabetic characters.")
        self.last_name = last_name

        if not lvl.isdigit() or int(lvl) not in range(1, 7):
            raise ValueError("Level must be an integer between 1 and 6.")
        self.lvl = int(lvl)

        if gender not in ('Male', 'Female', 'Other'):
            raise ValueError("Gender must be one of 'Male', 'Female', or 'Other'.")
        self.gender = gender

        if not course_code:
            raise ValueError("Course code cannot be empty.")
        self.course_code = course_code

class Course:
    def __init__(self, course_code, course_name):
        self.course_code = course_code
        self.course_name = course_name
    
    def __str__(self):
        return f'Course Code: {self.course_code}, Course Name: {self.course_name}'

class DatabaseManager:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )
            print("Connected to MySQL database")
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL database: {e}")

    def execute_query(self, query, params=None):
        if not self.connection:
            print("Error: Database connection is not established.")
            return None

        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()  
            self.connection.commit()
            return result
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return None
        
    def get_students(self):
        query = "SELECT * FROM students"
        return self.execute_query(query)
        
    def get_courses(self):
        query = "SELECT * FROM courses"
        return self.execute_query(query)
    
    def update_course_code_simultaneously(self, old_course_code, new_course_code):
        try:
            self.execute_query("SET FOREIGN_KEY_CHECKS=0")

            self.update_course_code(old_course_code, new_course_code)

            query = "UPDATE students SET course_code = %s WHERE course_code = %s"
            params = (new_course_code, old_course_code)
            self.execute_query(query, params)


            self.execute_query("SET FOREIGN_KEY_CHECKS=1")
        except Exception as e:
            print(f"Error updating course codes simultaneously: {e}")

    def update_course_code(self, old_course_code, new_course_code):
        try:
            query = "UPDATE courses SET course_code = %s WHERE course_code = %s"
            params = (new_course_code, old_course_code)
            self.execute_query(query, params)

        except Exception as e:
            print(f"Error updating course code: {e}")

    def update_course_name(self, course_code, new_course_name):
        query = "UPDATE courses SET course_name = %s WHERE course_code = %s"
        params = (new_course_name, course_code)
        self.execute_query(query, params)

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
    
    def add_foreign_key_constraint(self):
        query = "SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_NAME = 'fk_course_code' AND CONSTRAINT_SCHEMA = %s"
        params = (self.database,)
        result = self.execute_query(query, params)
        if result and result[0][0] > 0:
            print("Foreign key constraint 'fk_course_code' already exists.")
            return

        query = "ALTER TABLE students ADD CONSTRAINT fk_course_code FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE SET NULL"
        self.execute_query(query)
    


db_host = 'localhost'
db_username = 'root'
db_password = 'password' 
db_name = 'mydb'  
db_manager = DatabaseManager(db_host, db_username, db_password, db_name)
db_manager.connect()
db_manager.add_foreign_key_constraint()

class StudentManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_student(self, id_number, first_name, middle_name, last_name, lvl, gender, course_code):
        try:
            course_exists_query = "SELECT 1 FROM courses WHERE course_code = %s"
            course_exists_params = (course_code,)
            course_exists_result = self.db_manager.execute_query(course_exists_query, course_exists_params)
            
            if not course_exists_result:
                raise ValueError("Course code does not exist in the courses table.")

            existing_students = self.db_manager.get_students()
            if existing_students:
                for student in existing_students:
                    if student[0] == id_number:
                        raise ValueError("ID number already exists")

            query = "INSERT INTO students (id, first_name, middle_name, last_name, lvl, gender, course_code) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            params = (id_number, first_name, middle_name, last_name, lvl, gender, course_code)
            self.db_manager.execute_query(query, params)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except mysql.connector.Error as e:
            if e.errno == 1265 and e.sqlstate == '01000':
                messagebox.showerror("Error", "Data truncated for column 'gender'. Make sure gender data matches the column definition.")
            else:
                messagebox.showerror("Error", f"Database error: {e}")

    def delete_student(self, id_number):
        query = "DELETE FROM students WHERE id = %s"
        params = (id_number,)
        self.db_manager.execute_query(query, params)

    def update_student(self, id_number, first_name, middle_name, last_name, lvl, gender, course_code):
        try:
            if not re.match(r'^20\d{2}-\d{4}$', id_number):
                raise ValueError("Invalid ID format. Please use the format '20XX-XXXX'.")

            if not (lvl.isdigit() and 1 <= int(lvl) <= 6):
                raise ValueError("Invalid level. Please enter a number between 1 and 6.")
            query = "SELECT course_code FROM courses WHERE course_code = %s"
            params = (course_code,)
            result = self.db_manager.execute_query(query, params)
            if not result:
                raise ValueError("Course code does not exist in the courses table.")

            query = "UPDATE students SET first_name = %s, middle_name = %s, last_name = %s, lvl = %s, gender = %s, course_code = %s WHERE id = %s"
            params = (first_name, middle_name, last_name, lvl, gender, course_code, id_number)
            self.db_manager.execute_query(query, params)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def get_students(self):
        query = "SELECT * FROM students"
        rows = self.db_manager.execute_query(query)
        if rows:
            students = []
            for row in rows:
                student = Student(*row)
                students.append(student)
            return students
        return []


class CourseManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_course(self, course_code, course_name):
        course_code = course_code.upper()
        course_name = course_name.title()
        query = "INSERT INTO courses (course_code, course_name) VALUES (%s, %s)"
        params = (course_code, course_name)
        self.db_manager.execute_query(query, params)

    def delete_course(self, course_code):
        update_query = "UPDATE students SET course_code = NULL WHERE course_code = %s"
        self.db_manager.execute_query(update_query, (course_code,))

        delete_query = "DELETE FROM courses WHERE course_code = %s"
        self.db_manager.execute_query(delete_query, (course_code,))
            
    def get_courses(self):
        query = "SELECT * FROM courses"
        return self.db_manager.execute_query(query)

class AddStudentDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Student")

        self.id_label = ttk.Label(self.top, text="ID:")
        self.id_label.grid(row=0, column=0, padx=5, pady=5)
        self.id_entry = ttk.Entry(self.top)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)

        self.first_name_label = ttk.Label(self.top, text="First Name:")
        self.first_name_label.grid(row=1, column=0, padx=5, pady=5)
        self.first_name_entry = ttk.Entry(self.top)
        self.first_name_entry.grid(row=1, column=1, padx=5, pady=5)

        self.middle_name_label = ttk.Label(self.top, text="Middle Name:")
        self.middle_name_label.grid(row=2, column=0, padx=5, pady=5)
        self.middle_name_entry = ttk.Entry(self.top)
        self.middle_name_entry.grid(row=2, column=1, padx=5, pady=5)

        self.last_name_label = ttk.Label(self.top, text="Last Name:")
        self.last_name_label.grid(row=3, column=0, padx=5, pady=5)
        self.last_name_entry = ttk.Entry(self.top)
        self.last_name_entry.grid(row=3, column=1, padx=5, pady=5)

        self.level_label = ttk.Label(self.top, text="Year Level:")
        self.level_label.grid(row=4, column=0, padx=5, pady=5)
        self.level_var = tk.StringVar(self.top)
        self.level_var.set("") 
        self.level_option = ttk.OptionMenu(self.top, self.level_var,"", "1", "2", "3","4","5","6")
        self.level_option.grid(row=4, column=1, padx=5, pady=5)

        self.gender_label = ttk.Label(self.top, text="Gender:")
        self.gender_label.grid(row=5, column=0, padx=5, pady=5)
        self.gender_var = tk.StringVar(self.top)
        self.gender_var.set("") 
        self.gender_option = ttk.OptionMenu(self.top, self.gender_var,"", "Male", "Female", "Other")
        self.gender_option.grid(row=5, column=1, padx=5, pady=5)

        self.course_code_label = ttk.Label(self.top, text="Course Code:")
        self.course_code_label.grid(row=6, column=0, padx=5, pady=5)
        self.course_code_entry = ttk.Entry(self.top)
        self.course_code_entry.grid(row=6, column=1, padx=5, pady=5)

        self.submit_button = ttk.Button(self.top, text="Submit", command=self.submit)
        self.submit_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def submit(self):
        id_number = self.id_entry.get()
        first_name = self.first_name_entry.get().title()
        middle_name = self.middle_name_entry.get().title()
        last_name = self.last_name_entry.get().title()
        lvl = self.level_var.get()
        gender = GENDER_VALUES[self.gender_var.get()]
        course_code = self.course_code_entry.get()

        if not re.match(r'^20\d{2}-\d{4}$', id_number):
            messagebox.showerror("Error", "Invalid ID format. Please use the format '20XX-XXXX'.")
            return

        if not (lvl.isdigit() and 1 <= int(lvl) <= 6):
            messagebox.showerror("Error", "Invalid level. Please enter a number between 1 and 6.")
            return

        student_manager = StudentManager(db_manager) 
        student_manager.add_student(id_number, first_name, middle_name, last_name, lvl, gender, course_code)

        self.top.destroy()



class UpdateStudentDialog:
    def __init__(self, parent, student_data):
        self.top = tk.Toplevel(parent)
        self.top.title("Update Student")

        self.id_label = ttk.Label(self.top, text="ID:")
        self.id_label.grid(row=0, column=0, padx=5, pady=5)
        self.id_entry = ttk.Entry(self.top)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.id_entry.insert(0, student_data[0])
        self.id_entry.config(state='readonly')

        self.first_name_label = ttk.Label(self.top, text="First Name:")
        self.first_name_label.grid(row=1, column=0, padx=5, pady=5)
        self.first_name_entry = ttk.Entry(self.top)
        self.first_name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.first_name_entry.insert(0, student_data[1])

        self.middle_name_label = ttk.Label(self.top, text="Middle Name:")
        self.middle_name_label.grid(row=2, column=0, padx=5, pady=5)
        self.middle_name_entry = ttk.Entry(self.top)
        self.middle_name_entry.grid(row=2, column=1, padx=5, pady=5)
        self.middle_name_entry.insert(0, student_data[2])

        self.last_name_label = ttk.Label(self.top, text="Last Name:")
        self.last_name_label.grid(row=3, column=0, padx=5, pady=5)
        self.last_name_entry = ttk.Entry(self.top)
        self.last_name_entry.grid(row=3, column=1, padx=5, pady=5)
        self.last_name_entry.insert(0, student_data[3])

        self.level_label = ttk.Label(self.top, text="Year Level:")
        self.level_label.grid(row=4, column=0, padx=5, pady=5)
        self.level_var = tk.StringVar(self.top)
        self.level_var.set(student_data[4])
        self.level_option = ttk.OptionMenu(self.top, self.level_var, student_data[4], "1", "2", "3", "4", "5", "6")
        self.level_option.grid(row=4, column=1, padx=5, pady=5)

        self.gender_label = ttk.Label(self.top, text="Gender:")
        self.gender_label.grid(row=5, column=0, padx=5, pady=5)
        self.gender_var = tk.StringVar(self.top)
        self.gender_var.set(student_data[5])
        self.gender_option = ttk.OptionMenu(self.top, self.gender_var, student_data[5], "Male", "Female", "Other")
        self.gender_option.grid(row=5, column=1, padx=5, pady=5)

        self.course_code_label = ttk.Label(self.top, text="Course Code:")
        self.course_code_label.grid(row=6, column=0, padx=5, pady=5)
        self.course_code_entry = ttk.Entry(self.top)
        self.course_code_entry.grid(row=6, column=1, padx=5, pady=5)
        self.course_code_entry.insert(0, student_data[6])

        self.submit_button = ttk.Button(self.top, text="Submit", command=self.submit)
        self.submit_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def submit(self):
        id_number = self.id_entry.get()
        first_name = self.first_name_entry.get().title()
        middle_name = self.middle_name_entry.get().title()
        last_name = self.last_name_entry.get().title()
        lvl = self.level_var.get()
        gender = GENDER_VALUES[self.gender_var.get()]
        course_code = self.course_code_entry.get()

        if not re.match(r'^20\d{2}-\d{4}$', id_number):
            messagebox.showerror("Error", "Invalid ID format. Please use the format '20XX-XXXX'.")
            return

        if not (lvl.isdigit() and 1 <= int(lvl) <= 6):
            messagebox.showerror("Error", "Invalid level. Please enter a number between 1 and 6.")
            return

        query = "SELECT course_code FROM courses WHERE course_code = %s"
        params = (course_code,)
        result = db_manager.execute_query(query, params)
        if not result:
            messagebox.showerror("Error", "Course code does not exist in the courses table.")
            return

        student_manager = StudentManager(db_manager)
        student_manager.update_student(id_number, first_name, middle_name, last_name, lvl, gender, course_code)

        self.top.destroy()


class AddCourseDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Course")

        self.course_code_label = ttk.Label(self.top, text="Course Code:")
        self.course_code_label.grid(row=0, column=0, padx=5, pady=5)
        self.course_code_entry = ttk.Entry(self.top)
        self.course_code_entry.grid(row=0, column=1, padx=5, pady=5)

        self.course_name_label = ttk.Label(self.top, text="Course Name:")
        self.course_name_label.grid(row=1, column=0, padx=5, pady=5)
        self.course_name_entry = ttk.Entry(self.top)
        self.course_name_entry.grid(row=1, column=1, padx=5, pady=5)

        self.submit_button = ttk.Button(self.top, text="Submit", command=self.submit)
        self.submit_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def submit(self):

        course_code = self.course_code_entry.get()
        course_name = self.course_name_entry.get()

        course_manager = CourseManager(db_manager)
        course_manager.add_course(course_code, course_name)

        self.top.destroy()

class UpdateCourseDialog:
    def __init__(self, parent, course_data):
        self.top = tk.Toplevel(parent)
        self.top.title("Update Course")

        self.course_code_label = ttk.Label(self.top, text="Course Code:")
        self.course_code_label.grid(row=0, column=0, padx=5, pady=5)
        self.course_code_entry = ttk.Entry(self.top)
        self.course_code_entry.grid(row=0, column=1, padx=5, pady=5)
        self.course_code_entry.insert(0, course_data[0])

        self.course_name_label = ttk.Label(self.top, text="Course Name:")
        self.course_name_label.grid(row=1, column=0, padx=5, pady=5)
        self.course_name_entry = ttk.Entry(self.top)
        self.course_name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.course_name_entry.insert(0, course_data[1])

        self.submit_button = ttk.Button(self.top, text="Submit", command=self.submit)
        self.submit_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.original_course_data = course_data

    def submit(self):
        new_course_code = self.course_code_entry.get().upper()
        new_course_name = self.course_name_entry.get().title()

        if new_course_code != self.original_course_data[0]:
            try:
                db_manager.update_course_code_simultaneously(self.original_course_data[0], new_course_code)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update course code: {e}")
                return

        try:
            db_manager.update_course_name(new_course_code, new_course_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update course name: {e}")
            return

        self.top.destroy()
        app.reload_students()
        app.load_courses()


class Front:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.student_manager = StudentManager(db_manager)
        self.course_manager = CourseManager(db_manager)
        self.root.title("Student and Course Viewer")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.student_tab = ttk.Frame(self.notebook)
        self.course_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.student_tab, text='View Students')
        self.notebook.add(self.course_tab, text='View Courses')

        self.student_search_var = tk.StringVar()
        self.student_search_var.trace_add('write', self.filter_students)
        self.student_search_entry = ttk.Entry(self.student_tab, textvariable=self.student_search_var)
        self.student_search_entry.pack(fill='x', padx=10, pady=(10, 5))

        self.course_search_var = tk.StringVar()
        self.course_search_var.trace_add('write', self.filter_courses)
        self.course_search_entry = ttk.Entry(self.course_tab, textvariable=self.course_search_var)
        self.course_search_entry.pack(fill='x', padx=10, pady=(10, 5))

        self.student_label = ttk.Label(self.student_tab, text='Student Information')
        self.student_label.pack(pady=10)
        self.student_tree = ttk.Treeview(self.student_tab, columns=('ID', 'First Name', 'Middle Name', 'Last Name', 'Level', 'Gender', 'Course Code'), show='headings')
        self.student_tree.heading('ID', text='ID')
        self.student_tree.heading('First Name', text='First Name')
        self.student_tree.heading('Middle Name', text='Middle Name')
        self.student_tree.heading('Last Name', text='Last Name')
        self.student_tree.heading('Level', text='Level')
        self.student_tree.heading('Gender', text='Gender')
        self.student_tree.heading('Course Code', text='Course Code')
        self.student_tree.pack(fill='both', expand=True)

        self.student_buttons_frame = ttk.Frame(self.student_tab)
        self.student_buttons_frame.pack(pady=10)
        self.add_student_button = ttk.Button(self.student_buttons_frame, text='Add', command=self.add_student)
        self.add_student_button.grid(row=0, column=0, padx=5)
        self.delete_student_button = ttk.Button(self.student_buttons_frame, text='Delete', command=self.delete_student)
        self.delete_student_button.grid(row=0, column=1, padx=5)
        self.edit_student_button = ttk.Button(self.student_buttons_frame, text='Edit', command=self.edit_student)
        self.edit_student_button.grid(row=0, column=2, padx=5)

        self.course_label = ttk.Label(self.course_tab, text='Course Information')
        self.course_label.pack(pady=10)
        self.course_tree = ttk.Treeview(self.course_tab, columns=('Course Code', 'Course Name'), show='headings')
        self.course_tree.heading('Course Code', text='Course Code')
        self.course_tree.heading('Course Name', text='Course Name')
        self.course_tree.pack(fill='both', expand=True)

        self.course_buttons_frame = ttk.Frame(self.course_tab)
        self.course_buttons_frame.pack(pady=10)
        self.add_course_button = ttk.Button(self.course_buttons_frame, text='Add', command=self.add_course)
        self.add_course_button.grid(row=0, column=0, padx=5)
        self.delete_course_button = ttk.Button(self.course_buttons_frame, text='Delete', command=self.delete_course)
        self.delete_course_button.grid(row=0, column=1, padx=5)
        self.edit_course_button = ttk.Button(self.course_buttons_frame, text='Edit', command=self.edit_course)
        self.edit_course_button.grid(row=0, column=2, padx=5)

        self.load_students()
        self.load_courses()

    def reload_students(self):
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)

        students = self.db_manager.get_students()
        if students:
            for student in students:
                self.student_tree.insert('', 'end', values=student)

    def filter_students(self, *args):
        search_keyword = self.student_search_var.get().strip().lower()

        for row in self.student_tree.get_children():
            self.student_tree.delete(row)

        students = self.db_manager.get_students()
        if students:
            for student in students:
                if any(search_keyword in str(field).lower() for field in student):
                    self.student_tree.insert('', 'end', values=student)

    def filter_courses(self, *args):
        search_keyword = self.course_search_var.get().strip().lower()

        for row in self.course_tree.get_children():
            self.course_tree.delete(row)

        courses = self.db_manager.get_courses()
        if courses:
            for course in courses:
                if any(search_keyword in str(field).lower() for field in course):
                    self.course_tree.insert('', 'end', values=course)

    def load_students(self):
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)

        students = self.db_manager.get_students()
        if students:
            for student in students:
                gender = student[5]
                if gender == 'M':
                    gender = 'Male'
                elif gender == 'F':
                    gender = 'Female'
                else:
                    gender = 'Other'
                student = list(student)
                student[5] = gender
                self.student_tree.insert('', 'end', values=student)

    def load_courses(self):
        for row in self.course_tree.get_children():
            self.course_tree.delete(row)

        courses = self.db_manager.get_courses()
        if courses:
            for course in courses:
                self.course_tree.insert('', 'end', values=course)
    
    def add_student(self):
        dialog = AddStudentDialog(self.root)
        self.root.wait_window(dialog.top)

        self.load_students()

    def delete_student(self):
        selected_item = self.student_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student?")
        if confirm:
            student_id = self.student_tree.item(selected_item)['values'][0]

            self.student_manager.delete_student(student_id)

            self.load_students()

    def edit_student(self):
        selected_item = self.student_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to edit.")
            return

        student_data = self.student_tree.item(selected_item)['values']

        dialog = UpdateStudentDialog(self.root, student_data)
        self.root.wait_window(dialog.top)

        self.load_students()

    def add_course(self):
        dialog = AddCourseDialog(self.root)
        self.root.wait_window(dialog.top)

        self.load_courses()

    def delete_course(self):
        selected_item = self.course_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this course?")
        if confirm:
            course_id = self.course_tree.item(selected_item)['values'][0]

            self.course_manager.delete_course(course_id)

            self.load_courses()

            self.reload_students()


    def edit_course(self):
        selected_item = self.course_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to edit.")
            return

        course_data = self.course_tree.item(selected_item)['values']

        dialog = UpdateCourseDialog(self.root, course_data)
        self.root.wait_window(dialog.top)  
        self.load_courses() 

root = tk.Tk()
app = Front(root, db_manager)
root.mainloop()
