import sqlite3 #database
import numpy as np #encodings
import io #createing a data type called array in database
from datetime import date
import os
import cv2
from imgbeddings import imgbeddings
from PIL import Image


def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

def add_person(usn,name):
    if not name or not usn :
        return;
    try:
        cap = cv2.VideoCapture(0)
        success,frame = cap.read()
        if success:
            alg = "haarcascade_frontalface_alt2.xml"
            haar_cascade = cv2.CascadeClassifier(alg)
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = haar_cascade.detectMultiScale(gray_img, scaleFactor=1.05, minNeighbors=2, minSize=(100, 100))
            if(len(faces) > 1):
                print("too many faces detected")
            elif len(faces) == 1:
                x,y,w,h = faces[0]
                cropped_image = frame[y: y + h, x: x + w]
                path = "people\\"
                target_file_name = path + usn + ".jpg"
                cv2.imwrite(target_file_name,cropped_image)
                img = Image.open(target_file_name)
                ibed = imgbeddings()
                embedding = ibed.to_embeddings(img)[0]
                sqlite3.register_adapter(np.ndarray, adapt_array)
                sqlite3.register_converter("array", convert_array)
                con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
                cur = con.cursor()
                cur.execute("""INSERT INTO Face values (?,?,?,?,?,?);""", (usn, name, embedding, 0, 0,''))
                con.commit()
                con.close()
            else:
                print("No face Detected")
        else:
            print("Camera Failure")
    except Exception as e:
        print(e)

def check_attendance():
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("""
        SELECT USN, NAME, ATTENDANCE, PERCENTAGE, DATE FROM FACE;
    """)
    details = cur.fetchall()
    return details

def delete_person(usn):
    if not usn:
        return;

    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("DELETE FROM Face WHERE USN = ?;",(usn,))
    con.commit()
    con.close()
    path = "people\\"
    target_file_name = path + usn + ".jpg"
    os.remove(target_file_name)

def take_attendance():
    l = []
    try:
        while len(l) == 0:
            count = 0
            alg = "haarcascade_frontalface_alt2.xml"
            haar_cascade = cv2.CascadeClassifier(alg)
            cap = cv2.VideoCapture(0)
            success, img = cap.read()
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = haar_cascade.detectMultiScale(gray_img, scaleFactor=1.25, minSize=(100, 100))
            i = 0
            for x, y, w, h in faces:
                cropped_image = img[y: y + h, x: x + w]
                target_file_name = 'seen\\' + str(i) + ".jpg"
                cv2.imwrite(target_file_name, cropped_image)
                i += 1
                image = Image.open(target_file_name)
                ibed = imgbeddings()
                test_encoding = ibed.to_embeddings(image)[0]
                l.append(test_encoding)
    except Exception as e:
        print(e)
    return l

def closest_array(input_array, candidate_arrays):
    closest_idx = None
    min_distance = float('inf')

    for idx, arr in enumerate(candidate_arrays):
        distance = np.linalg.norm(input_array - arr)
        if distance < min_distance:
            min_distance = distance
            closest_idx = idx

    return candidate_arrays[closest_idx]

def read_Encodings():
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("Select ENCODINGS from Face;")
    con.commit()
    c = cur.fetchall()
    con.close()
    return c

def fetch_USN(vector):
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("SELECT USN FROM Face WHERE ENCODINGS = ?;", (vector,))
    c = cur.fetchone()
    con.commit()
    con.close()
    return c

def max_date():
    l = []
    with open('total_days.txt','r') as f:
        latest_date,days = f.readlines()
        update_all(int(days))
        if(latest_date < str(date.today())):
            l = [0,0,0]
            days = int(days) + 1
            l[2] = str(days)
            l[1] = '\n'
            l[0] = str(date.today())
    if(len(l) == 3):
        with open('total_days.txt','w') as f:
            f.writelines(l)
    return days

def update_all(total_days):
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("""
            SELECT ATTENDANCE,USN FROM FACE;
        """)
    con.commit()
    l = np.array(cur.fetchall())
    for i in l:
        i[0] = str(int(i[0])/total_days * 100 )
        cur.execute("UPDATE FACE SET PERCENTAGE = ? WHERE USN  = ?",(i[0],i[1]))
        con.commit()
    con.close()

def update_attendance(usn):
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("Select DATE,ATTENDANCE  from Face WHERE USN =?;",(usn,))
    con.commit()
    latest_marked_date,days_present = cur.fetchone()
    total_days = max_date()
    todays_date = str(date.today())
    if(latest_marked_date == "" or todays_date > latest_marked_date):
        days_present = int(days_present) + 1
        percentage = days_present/int(total_days) * 100
        cur.execute("UPDATE Face  SET DATE = ?, ATTENDANCE = ?, PERCENTAGE = ? WHERE USN = ?;",
                    (date.today(),days_present,percentage,usn))
        con.commit()
        con.close()
    else:
        print(f"Already makred {usn}")

def mark_attendance():
    people_seen  = take_attendance()
    people_in_class = read_Encodings()
    for i in people_seen:
        encoding = closest_array(i,people_in_class)
        usn = fetch_USN(encoding[0])[0]
        update_attendance(usn)


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')


def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return frame, faces


def generate_frames():
    camera = cv2.VideoCapture(0)  # Open default camera (0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame, _ = detect_faces(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

