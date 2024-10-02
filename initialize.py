import datetime
import os
import sqlite3
import io
import numpy as np


def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


def folders():
    directory1 = 'people'
    directory2 = 'seen'
    if not os.path.exists(directory1):
        os.makedirs(directory1)
        print(f"Directory '{directory1}' created.")
    else:
        print(f"Directory '{directory1}' already exists.")

    if not os.path.exists(directory2):
        os.makedirs(directory2)
        print(f"Directory '{directory2}' created.")
    else:
        print(f"Directory '{directory2}' already exists.")


def create_table():
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Face(
                    USN CHAR NOT NULL PRIMARY KEY,
                    NAME CHAR NOT NULL,
                    ENCODINGS array NOT NULL,
                    ATTENDANCE INTEGER NOT NULL,
                    PERCENTAGE REAL NOT NULL,
                    DATE TEXT);""")
    con.commit()
    con.close()



def text_file():
    with open('total_days.txt', 'w') as f:
        l = [0, 0, 0]
        l[0] = str(datetime.date.today())
        l[1] = '\n'
        l[2] = '1'
        f.writelines(l)


def init():
    folders()
    create_table()
    text_file()


def delete_table():
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect('Face_encodings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("""DROP TABLE Face;""")
    con.commit()
    con.close()

def delete():
    delete_table()
    for i in os.listdir('people'):
        os.remove(i)
    os.rmdir('people')
    for i in os.listdir('seen'):
        os.remove(i)
    os.rmdir('seen')

#uncomment below line to initiaize
#init()

#uncomment below line to destroy database file,seen and people folders
#delete()