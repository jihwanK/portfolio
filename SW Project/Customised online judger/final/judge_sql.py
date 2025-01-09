import sqlite3
import sys
import time
import datetime
import json


#################################################################################################################################
# check if the student_sql includes such like "insert", "update", "delete", "drop", "alter" that can modify the database itself #
#################################################################################################################################

def check_sql(instructor_sql, student_sql):
    lower_sql = student_sql.lower()
    if "insert" in lower_sql or "update" in lower_sql or "delete" in lower_sql or "drop" in lower_sql or "alter" in lower_sql:
        return (21, 'SHOULD NOT USE insert, update, delete, drop, alter')
    try:
        cur.execute(student_sql)
        result_value = cur.fetchall()
        result_field = [des[0] for des in cur.description]
        conn.commit()
        return (result_value, result_field)
    except sqlite3.Error as e:
        if instructor_sql == student_sql:
            return (22, 'the instructors sql is wrong, ' + e.message)
        else:
            return (2, e.message)


#####################
# fetch the results #
#####################

def fetch_result(sql):
    cur.execute(sql)
    result_value = cur.fetchall()
    result_field = [des[0] for des in cur.description]
    conn.commit()

    return (result_value, result_field)


#########################
# get dictionary result #
#########################

def make_dict(query_result, columns):
    result = {}

    for j in range(len(columns)):
        col_data = []
        for i in range(len(query_result)):
            col_data.append(query_result[i][j])
        result[columns[j]] = col_data

    return result


#########################
# get the answer result #
#########################

def get_result(sql):
    cur.execute(sql)
    conn.commit()

    query_result = cur.fetchall()
    
    if len(query_result) == 0:
        return (False, '')

    columns = [des[0] for des in cur.description]
    result = make_dict(query_result, columns)

    return (result, columns)


########################################################################
# compare the results from one from instructor, the other from student #
########################################################################

def compare_results(result_instructor, result_student):
    # first, check whether the reuslt is empty set 
    if result_instructor is not False and result_student is not False:
        pass
    elif result_instructor is False and result_student is False:
        return 0
    elif result_instructor is False and result_student is not False:
        return 13
    elif result_instructor is not False and result_student is False:
        return 14

    # second, check if the number of columns is same
    if len(result_instructor.keys()) != len(result_student.keys()):
        return 11

    # third, check if the number of rows is same
    if len(result_instructor.values()[0]) != len(result_student.values()[0]):
        return 12

    # finally, if those are same, compare the values
    for key_instructor in result_instructor.keys():
        for key_student in result_student.keys():
            if result_instructor[key_instructor] == result_student[key_student]:
                result_instructor.pop(key_instructor)
                result_student.pop(key_student)
                break

    if len(result_student.keys()) == 0:
        return 0
    else: return 17


##############################################################################
# compare the result of student's sql to instructor's using 'except' keyword #
##############################################################################

def compare_using_sql(instructor_sql, student_sql):
    sql1 = 'select * from ({instructor}) EXCEPT select * from ({student})'.format(instructor=instructor_sql, student=student_sql)
    sql2 = 'select * from ({student}) EXCEPT select * from ({instructor})'.format(instructor=instructor_sql, student=student_sql)

    try:
        cur.execute(sql1)
    except sqlite3.Error as e:
        print(e.message)
        return (2, 'sql1 at compare_using_sql has problems => ' + e.message)
   
    res1 = cur.fetchall()

    if len(res1) != 0:
        return (15, 'the result of instructor - the result of student != empty set')

    try:
        cur.execute(sql2)
    except sqlite3.Error as e:
        print(e.message)
        return (2, 'sql2 at compare_using_sql has problems: ' + e.message)

    res2 = cur.fetchall()

    conn.commit()

    if len(res2) == 0:
        return 0
    else:
        return (16, 'the result of student - the result of instructor != empty set')



def handle_the_result(code, result_values=(), error_message=''):
    if code == 0:
        # correct
        print('correct')
        result = json.dumps({ 'result_code': code, 'result': 0, 'result_value': result_values[0], 'result_field': result_values[1] })
        return result
    elif code == 11:
        # the number of columns between instructor and student is different
        print('the number of columns between instructor and student is different')
        result = json.dumps({ 'result_code': code, 'result': 1, 'result_value': result_values[0], 'result_field': result_values[1], 'error': 'the number of columns between instructor and student is different' })
        return result
    elif code == 12:
        # the number of rows between instructor and student is different
        print('the number of rows between instructor and student is different')
        result = json.dumps({ 'result_code': code, 'result': 1, 'result_value': result_values[0], 'result_field': result_values[1], 'error': 'the number of rows between instructor and student is different' })
        return result
    elif code == 13:
        # the number of results from instructor is zero but not student's
        print("the number of results from instructor is zero but not student's")
        result = json.dumps({ 'result_code': code, 'result': 1, 'result_value': result_values[0], 'result_field': result_values[1], 'error': 'the result of the instructor is an empty set but not that of the student' })
        return result
    elif code == 14:
        # the number of results from student is zero but not instructor's
        print("the number of results from student is zero but not instructor's")
        result = json.dumps({ 'result_code': code, 'result': 1, 'result_value': result_values[0], 'result_field': result_values[1], 'error': 'the result of the student is an empty set but not that of the instructor' })
        return result
    elif code == 15:
        # the result of instructor - the result of student != empty set
        print("the result of instructor - the result of student != empty set")
        result = json.dumps({ 'result_code': code, 'result': 1, 'result_value': result_values[0], 'result_field': result_values[1], 'error': error_message })
        return result
    elif code == 16:
        # the result of student - the result of instructor != empty set
        print("the result of student - the result of instructor != empty set")
        result = json.dumps({ 'result_code': code, 'result': 1, 'result_value': result_values[0], 'result_field': result_values[1], 'error': error_message })
        return result
    elif code == 17:
        # the result is wrong, ORDER BY
        print("the result is wrong, ORDER BY")
        result = json.dumps({ 'result_code': code, 'result': 1, 'result_value': result_values[0], 'result_field': result_values[1], 'error': 'the result on ORDER BY is wrong' })
        return result
    elif code == 2:
        # it companied error message, we can make json using error message
        print('error')
        print(error_message)
        result = json.dumps({ 'result_code': code, 'result': 2, 'error': error_message })
        return result
    elif code == 21:
        # student tried to use banned queries
        print('error')
        print('student tried to use one of the banned queries')
        result = json.dumps({ 'result_code': code, 'result': 2, 'error': 'student tried to use one of the banned queries' })
        return result
    elif code == 22:
        # the student's sql is same as instructor's but the original intructor's sql is wrong
        print('error')
        print(error_message)
        result = json.dumps({ 'result_code': code, 'result': 2, 'error': error_message })
        return result


#################
# main function #
#################

def start(instructor_sql, student_sql):
    # check the sql
    result_values = check_sql(instructor_sql, student_sql)
    if result_values[0] == 21 or result_values[0] == 2 or result_values[0] == 22:
        return handle_the_result(code=result_values[0], error_message=result_values[1] )

    # compare the sql before analyzing
    if instructor_sql == student_sql:
        print("correct")
        return handle_the_result(code=0, result_values=result_values)

    if 'ORDER BY' in instructor_sql.upper():
        # print result_values
        result_instructor = get_result(instructor_sql)
        result_student = get_result(student_sql)
        compared = compare_results(result_instructor[0], result_student[0])
        return handle_the_result(code=compared, result_values=result_values)
    else:        
        res = compare_using_sql(instructor_sql, student_sql)
        if res == 0:
            return handle_the_result(code=res, result_values=result_values)
        else: return handle_the_result(code=res[0], result_values=result_values, error_message=res[1])


conn = sqlite3.connect('example.db')
cur = conn.cursor()

start(sys.argv[1], sys.argv[2])

cur.close()
conn.close()