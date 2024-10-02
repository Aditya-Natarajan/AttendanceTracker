from functions import *
from flask import Flask, render_template, Response, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/remove')
def remove_page():
    return render_template('remove_student.html')


@app.route('/remove_student', methods=['POST'])
def rmv_stud():
    try:
        if request.method == 'POST':
            usn_to_delete = request.form['usn']
            delete_person(usn_to_delete)
    except Exception as e:
        print(e)
    return render_template("/remove_student.html")


@app.route('/add')
def add_page():
    return render_template('add_student.html')


@app.route('/add_student', methods=['POST'])
def add_stud():
    try:
        if request.method == 'POST':
            name = request.form['name']  # Get data from first textbox (name)
            usn = request.form['usn']  # Get data from second textbox (usn)
            add_person(usn, name)  # Call your function with the parameters
    except Exception as e:
        print(e)
    return render_template('add_student.html')


@app.route('/mark')
def take_attendance_page():
    return render_template('mark_student.html')


@app.route('/mark_attendance')
def take_attend():
    mark_attendance()
    return render_template('mark_student.html')


@app.route('/check')
def check_attendance_page():
    return render_template('attendencelist.html', my_list=check_attendance())


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')