import mysql.connector
import sys
import os
from datetime import date, datetime, timedelta

user='oj'
password='oj1234'
database='oj'

conn = mysql.connector.connect(user=user, password=password, database=database)
cur = conn.cursor()

def create_problem(problem_title):
    SQL = "INSERT INTO problem (title, time_limit, memory_limit) VALUES (%(title)s, %(time_limit)s, %(memory_limit)s);"
    problem_data = {
        'title': problem_title,
        'time_limit': 1,
        'memory_limit': 256
    }
    cur.execute(SQL, problem_data)
    
def get_source_code(file):
    code = ''
    with open (file, 'r') as rs:
        lines = rs.readlines()
        for line in lines:
            code = code + line
        rs.close()
    return code

def insert_source(file):
    code = get_source_code(file)
    SQL = "INSERT INTO source_code (source) VALUES (%(code)s);"
    source_data = {
        'code': code
    }
    cur.execute(SQL, source_data)

def insert_solution(problem_number, language):
    SQL = "INSERT INTO solution (problem_id, user_id, language, in_date, ip) VALUES (%(id)s, %(user)s, %(lang)s, %(date)s, %(ip)s);"
    date = datetime.now()
    formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
    solution_data = {
        'id': problem_number,
        'user': 'jhwan',
        'lang': language,
        'date': formatted_date,
        'ip': '0.0.0.0'
    }
    cur.execute(SQL, solution_data)

def submit(file, problem_number, language):
    insert_source(file)
    insert_solution(problem_number, language)

##################################################################

if sys.argv[1] == 'problem':
    if len(sys.argv) != 3:
        print("SYNTAX ERROR OCCURS")
        print("USAGE: python problem [title]")
        exit(-1)
    else:
        create_problem(sys.argv[2])
elif sys.argv[1] == 'source':
    if len(sys.argv) != 3:
        print("SYNTAX ERROR OCCURS")
        print("USAGE: python source [file_path]")
        exit(-1)
    else:
        insert_source(sys.argv[2])
elif sys.argv[1] == 'solution':
    if len(sys.argv) != 4:
        print("SYNTAX ERROR OCCURS")
        print("USAGE: python solution [problem_id] [language_code]")
        exit(-1)
    else:
        insert_solution(sys.argv[2])
elif sys.argv[1] == 'submit':
    if len(sys.argv) != 5:
        print("SYNTAX ERROR OCCURS")
        print("USAGE: python submit [file_path] [problem_id] [language_code]")
        exit(-1)
    else:
        submit(sys.argv[2], sys.argv[3], sys.argv[4])
else:
    print("SYNTAX ERROR OCCURS")
    print("USAGE: python [problem|submit|source|submit]")
    exit(-1)

conn.commit()
cur.close()
conn.close()
