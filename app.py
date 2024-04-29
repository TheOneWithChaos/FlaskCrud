from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://root:1234@localhost/crud')
connection = engine.connect()
app = Flask(__name__) 
app.secret_key = "MY SECRET KEY" 

@app.route("/") 
def index():
    result = connection.execute(text("""
        SELECT students.id, students.name, students.email, students.phone, GROUP_CONCAT(subjects.name) as subjects
        FROM students
        LEFT JOIN student_subjects ON students.id = student_subjects.student_id
        LEFT JOIN subjects ON student_subjects.subject_id = subjects.id
        GROUP BY students.id
    """))
    return render_template('index.html', students = result)

@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        connection.execute(text(f"INSERT INTO students (name, email, phone) VALUES ('{name}', '{email}', '{phone}')"))
        connection.commit()
        flash("Data Inserted Successfully")
        return redirect(url_for('index'))

    
@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    connection.execute(text(f"DELETE FROM students WHERE id = {id_data}"))
    connection.commit()
    flash("Record Has Been Deleted Successfully")
    return redirect(url_for('index'))

@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        connection.execute(text(f"UPDATE students SET name = '{name}', email = '{email}', phone = '{phone}' WHERE id = {id_data}"))
        connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('student_page', student_id=id_data))
    # student = connection.execute(text(f"SELECT * FROM students WHERE id = {id}")).fetchone()
    # return render_template('index.html', student=student)

@app.route("/subjects") 
def subjects():
    result = connection.execute(text("SELECT * FROM subjects"))
    return render_template('subjects.html', subjects = result)

@app.route('/insert_subject', methods = ['POST'])
def insert_subject():
    if request.method == 'POST':
        name = request.form['name']
        connection.execute(text(f"INSERT INTO subjects (name) VALUES ('{name}')"))
        flash("Subject Inserted Successfully")
    result = connection.execute(text("SELECT * FROM subjects"))
    return render_template('subjects.html', subjects = result)


@app.route('/delete_subject/<string:id>', methods = ['GET'])
def delete_subject(id):
    connection.execute(text(f"DELETE FROM student_subjects WHERE subject_id = {id}"))
    connection.execute(text(f"DELETE FROM subjects WHERE id = {id}"))
    flash("Subject Deleted Successfully")
    return redirect(url_for('subjects'))

@app.route('/update_subject/<string:id>', methods = ['GET', 'POST'])
def update_subject(id):
    if request.method == 'POST':
        name = request.form['name']
        connection.execute(text(f"UPDATE subjects SET name = '{name}' WHERE id = {id}"))
        flash("Subject Updated Successfully")
        return redirect(url_for('subjects'))
    result = connection.execute(text(f"SELECT * FROM subjects WHERE id = {id}"))
    return render_template('update_subject.html', subject = result.first())

@app.route("/student/<string:student_id>")
def student_page(student_id):
    student = connection.execute(text(f"SELECT * FROM students WHERE id = {student_id}")).fetchone()
    subjects = connection.execute(text(f"SELECT s.name, s.id FROM subjects s JOIN student_subjects ss ON s.id = ss.subject_id WHERE ss.student_id = {student_id}")).fetchall()
    all_subjects = connection.execute(text("SELECT * FROM subjects")).fetchall()
    student_subjects = connection.execute(text(f"""
        SELECT s.id, s.name
        FROM subjects s
        LEFT JOIN student_subjects ss ON s.id = ss.subject_id
        WHERE ss.student_id = :student_id
    """), {"student_id": student_id}).fetchall() 
    available_subjects = [subject for subject in all_subjects if subject not in student_subjects]
    return render_template('student.html', student=student, subjects=subjects, available_subjects=available_subjects)

@app.route('/add_subject_to_student/<string:student_id>', methods=['POST'])
def add_subject_to_student(student_id):
    all_subjects = connection.execute(text("SELECT * FROM subjects")).fetchall()
    student_subjects = connection.execute(text(f"""
        SELECT s.id, s.name
        FROM subjects s
        LEFT JOIN student_subjects ss ON s.id = ss.subject_id
        WHERE ss.student_id = :student_id
    """), {"student_id": student_id}).fetchall() 
    available_subjects = [subject for subject in all_subjects if subject not in student_subjects]
    subject_id = request.form['subject_id']
    connection.execute(text(f"INSERT INTO student_subjects (student_id, subject_id) VALUES ({student_id}, {subject_id})"))   
    flash("Subject added successfully")
    return redirect(url_for('student_page', student_id=student_id, available_subjects=available_subjects))

@app.route('/remove_subject_from_student/<string:student_id>', methods=['POST'])
def remove_subject_from_student(student_id):
    subject_id = request.form['subject_id']
    connection.execute(text(f"DELETE FROM student_subjects WHERE student_id = {student_id} AND subject_id = {subject_id}"))
    flash("Subject removed successfully")
    return redirect(url_for('student_page', student_id=student_id))

if __name__ == '__main__':
    app.run(debug=True)

