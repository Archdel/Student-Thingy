from flask import Flask, render_template, request, redirect, url_for, flash
from db_manager import db_manager   # Import your DB manager logic
from student_manager import StudentManager
from course_manager import CourseManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'

student_manager = StudentManager(db_manager)
course_manager = CourseManager(db_manager)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def view_students():
    students = student_manager.get_students()
    return render_template('students.html', students=students)

@app.route('/courses')
def view_courses():
    courses = course_manager.get_courses()
    return render_template('courses.html', courses=courses)

# Add a student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_data = {
            'id_number': request.form['id_number'],
            'first_name': request.form['first_name'],
            'middle_name': request.form['middle_name'],
            'last_name': request.form['last_name'],
            'level': request.form['level'],
            'gender': request.form['gender'],
            'course_code': request.form['course_code']
        }
        student_manager.add_student(**student_data)
        flash('Student added successfully!')
        return redirect(url_for('view_students'))
    return render_template('add_student.html')

# Update student
@app.route('/edit_student/<string:id_number>', methods=['GET', 'POST'])
def edit_student(id_number):
    student = student_manager.get_student(id_number)
    if request.method == 'POST':
        student_data = {
            'id_number': id_number,
            'first_name': request.form['first_name'],
            'middle_name': request.form['middle_name'],
            'last_name': request.form['last_name'],
            'level': request.form['level'],
            'gender': request.form['gender'],
            'course_code': request.form['course_code']
        }
        student_manager.update_student(**student_data)
        flash('Student updated successfully!')
        return redirect(url_for('view_students'))
    return render_template('edit_student.html', student=student)

# Delete student
@app.route('/delete_student/<string:id_number>', methods=['POST'])
def delete_student(id_number):
    student_manager.delete_student(id_number)
    flash('Student deleted successfully!')
    return redirect(url_for('view_students'))

# Add course
@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_data = {
            'course_code': request.form['course_code'],
            'course_name': request.form['course_name']
        }
        course_manager.add_course(**course_data)
        flash('Course added successfully!')
        return redirect(url_for('view_courses'))
    return render_template('add_course.html')

# Update course
@app.route('/edit_course/<string:course_code>', methods=['GET', 'POST'])
def edit_course(course_code):
    course = course_manager.get_course(course_code)
    if request.method == 'POST':
        course_data = {
            'course_code': request.form['course_code'],
            'course_name': request.form['course_name']
        }
        course_manager.update_course(**course_data)
        flash('Course updated successfully!')
        return redirect(url_for('view_courses'))
    return render_template('edit_course.html', course=course)

# Delete course
@app.route('/delete_course/<string:course_code>', methods=['POST'])
def delete_course(course_code):
    course_manager.delete_course(course_code)
    flash('Course deleted successfully!')
    return redirect(url_for('view_courses'))

if __name__ == '__main__':
    app.run(debug=True)
