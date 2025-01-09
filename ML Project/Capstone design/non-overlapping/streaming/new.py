import psycopg2

##############
# log scheme #
##############

# [0]: timestamp
# [1]: cctv_id
# [2]: tracklet
# [3]: grid
# [4]: size
# [5]: speed

def start():
    global conn
    global cur
    global entry_log_buffer
    global exit_log_buffer
    global buffer
    global candidates

    entry_log_buffer = []
    exit_log_buffer = []
    buffer = dict()
    candidates = []

    conn = psycopg2.connect(host="localhost", database="mct", user="mct", password="password")
    # conn = psycopg2.connect(host="localhost", database="mct_streaming", user="mct", password="password")
    cur = conn.cursor()

def finish():
    cur.close()
    conn.close()


def push_the_raw_log(log, exit_entry):
    sql = '''INSERT INTO exit_entry_log (timestamp, cctv_id, tracklet_id, grid_id, speed, size, exit_entry) 
    VALUES (%(timestamp)s, %(cctv_id)s, %(tracklet_id)s, %(grid_id)s, %(speed)s, %(size)s, %(exit_entry)s)
    '''
    data = {
        'timestamp': log[0],
        'cctv_id': log[1],
        'tracklet_id': log[2],
        'grid_id': log[3],
        'speed': log[5],
        'size': log[4],
        'exit_entry': exit_entry,
    }
    cur.execute(sql, data)
    conn.commit()
 

def get_grid_metric(cctv_a, grid_a, cctv_b, grid_b):
    sql = '''
    SELECT T.cnt/B.cnt AS rate
    FROM
        (SELECT cctv_a_id, grid_a_id, sum(count) AS cnt
        FROM link_info
        GROUP BY (cctv_a_id, grid_a_id)) AS B,
        (SELECT cctv_a_id, grid_a_id, cctv_b_id, grid_b_id, count AS cnt
        FROM link_info
        WHERE (cctv_a_id=%(cctv_a)s AND grid_a_id=%(grid_a)s AND cctv_b_id=%(cctv_b)s AND grid_b_id=%(grid_b)s)
        OR (cctv_a_id=%(cctv_b)s AND grid_a_id=%(grid_b)s AND cctv_b_id=%(cctv_a)s AND grid_b_id=%(grid_a)s)) AS T
    WHERE B.cctv_a_id=T.cctv_a_id AND B.grid_a_id=T.grid_a_id
    '''
    data = {
        'cctv_a': cctv_a, 
        'grid_a': grid_a,
        'cctv_b': cctv_b,
        'grid_b': grid_b,
    }
    cur.execute(sql, data)
    result = cur.fetchone()

    return float(result[0])


def get_metric_info(cctv_a, grid_a, cctv_b, grid_b):
    sql = '''
    SELECT speed_variation_rate, size_variation_rate FROM link_info
    WHERE (cctv_a_id=%(cctv_a)s AND grid_a_id=%(grid_a)s AND cctv_b_id=%(cctv_b)s AND grid_b_id=%(grid_b)s)
        OR (cctv_a_id=%(cctv_b)s AND grid_a_id=%(grid_b)s AND cctv_b_id=%(cctv_a)s AND grid_b_id=%(grid_a)s)
    '''
    data = {
        'cctv_a': cctv_a, 
        'grid_a': grid_a, 
        'cctv_b': cctv_b, 
        'grid_b': grid_b,
    }
    cur.execute(sql, data)
    result = cur.fetchone()

    return result


def get_link_info(cctv_id):
    # this thread is waiting for the entry log to make a pair with exit log
    # life cycle will be calculated upper
    # after the upper, this thread will be expired
    sql = '''
    SELECT cctv_a_id AS cctv_id FROM LINK_INIT WHERE cctv_b_id=%(cctv_id)s
    UNION
    SELECT cctv_b_id AS cctv_id FROM LINK_INIT WHERE cctv_a_id=%(cctv_id)s
    '''
    data = {
        'cctv_id': cctv_id,
    }
    cur.execute(sql, data)
    results = cur.fetchall()
    # cctv_id, t_lower, t_upper
    
    return results


def get_timegaps(cctv_a, grid_a, cctv_b, grid_b):
    sql = '''
    SELECT time_lower_bound, time_upper_bound FROM link_info
    WHERE (cctv_a_id=%(cctv_a)s AND grid_a_id=%(grid_a)s AND cctv_b_id=%(cctv_b)s AND grid_b_id=%(grid_b)s)
        OR (cctv_a_id=%(cctv_b)s AND grid_a_id=%(grid_b)s AND cctv_b_id=%(cctv_a)s AND grid_b_id=%(grid_a)s)
    '''
    data = {
        'cctv_a': cctv_a, 
        'grid_a': grid_a, 
        'cctv_b': cctv_b, 
        'grid_b': grid_b,
    }
    cur.execute(sql, data)
    result = cur.fetchone()

    return result


def algorithm(line):
    unit_time = 1_000

    segmented_log = line.split('\t')
    if segmented_log[1] == '1':

        key = (segmented_log[2], segmented_log[0]) # tracklet_key = (cctv_id, tracklet_id)

        grids = segmented_log[4].split(',')
        sizes = segmented_log[5].split(',')
        speeds = segmented_log[9].split(',')

        log = ([segmented_log[3],], segmented_log[2], segmented_log[0], grids, sizes, speeds)
        entry_log = (int(segmented_log[3]), int(segmented_log[2]), int(segmented_log[0]), int(grids[0]), float(sizes[0]), float(speeds[0]))

        # 같은 cctv에서 인접하는 다수의 exit logs의 timegap이 특정시간 이내이면 (e.g. 1000ms) learning 하지 않음.

        # insert new exit log
        for buffer_log in buffer.values():
            if (int(segmented_log[3]) - int(buffer_log[0][-1])) > unit_time:
                buffer.pop( (buffer_log[1], buffer_log[2]) )
                if buffer_log[5][-1] == '-1':
                    if buffer_log[5][len(buffer_log[5])-2] == '-1':
                        speed = buffer_log[5][len(buffer_log[5])-3]
                    else:   
                        speed = buffer_log[5][len(buffer_log[5])-2]
                else:
                    speed = buffer_log[5][-1]

                exit_log = (int(buffer_log[0][-1])+500, int(buffer_log[1]), int(buffer_log[2]), int(buffer_log[3][-1]), float(buffer_log[4][-1]), float(speed))
                exit_log_buffer.append(exit_log)
                # push_the_raw_log(exit_log, 'exit')
                break

        # insert new entry log 
        connectable_tracklet = []

        if key not in buffer.keys():
            buffer[key] = log
            entry_log_buffer.append(entry_log)
            # push_the_raw_log(entry_log, 'entry')

            if len(exit_log_buffer) > 0:
                candidates = []

                for entry_log in entry_log_buffer:
                    link_infos = get_link_info(entry_log[1])
                    min_timegap = 987_654_321
                    s_entry = ()
                    s_exit = ()
                    
                    for exit_log in exit_log_buffer:
                        for link in link_infos:    
                            if (exit_log[1] == link[0]) and (0 < (entry_log[0] - exit_log[0]) < min_timegap):
                                min_timegap = int(entry_log[0]) - int(exit_log[0])
                                s_entry = entry_log
                                s_exit = exit_log

                    if (len(s_exit) != 0) and (len(s_entry) != 0):
                        exit_log_buffer.remove(s_exit)
                        entry_log_buffer.remove(s_entry)
                        candidates.append( (s_entry, s_exit) )

                if len(candidates) != 0:
                    max_final_score = -987_654_321
                    for candidate in candidates:
                        time_bound = get_timegaps(candidate[0][1], candidate[0][3], candidate[1][1], candidate[1][3])
                        if time_bound is None:
                            continue
                        else:
                            lower, upper = time_bound

                        if (lower < abs(candidate[0][0] - candidate[1][0]) < upper):
                            speed_rate, size_rate = get_metric_info(candidate[0][1], candidate[0][3], candidate[1][1], candidate[1][3])
                            grid_score = get_grid_metric(candidate[0][1], candidate[0][3], candidate[1][1], candidate[1][3])
                            final_score = get_final_score(speed_rate, size_rate, grid_score, candidate)

                            # print('final:', final_score)

                            if max_final_score < final_score:
                                max_final_score = final_score
                                connectable_tracklet.append((candidate, max_final_score))
                            
                            print('max:', max_final_score)

                            # print('differnce ==>', max_final_score - final_score)
                
                        # print(max_final_score, candidate)
        else:
            timestamp, cctv_id, tracklet_id, grid_list, size_list, speed_list = buffer[key]
            timestamp.extend(log[0])
            grid_list.extend(log[3])
            size_list.extend(log[4])
            speed_list.extend(log[5])
            updated_log = (timestamp, cctv_id, tracklet_id, grid_list, size_list, speed_list)
            buffer[key] = updated_log
        
        if len(connectable_tracklet) != 0:
            connet_tracklet(connectable_tracklet[0][0], connectable_tracklet[0][1])





###################
# exit_entry_link #
###################

# def connet_tracklet(connectable_tracklet, score):
#     sql = '''
#     SELECT trajectory_id FROM exit_entry_link 
#     WHERE (cctv_a_id=%(cctv_a)s AND tracklet_a_id=%(tracklet_a)s)
#         OR (cctv_b_id=%(cctv_b)s AND tracklet_b_id=%(tracklet_b)s)
#         OR (cctv_a_id=%(cctv_b)s AND tracklet_a_id=%(tracklet_b)s)
#         OR (cctv_b_id=%(cctv_a)s AND tracklet_b_id=%(tracklet_a)s)
#     '''
#     if connectable_tracklet[0][1] < connectable_tracklet[1][1]:
#         data = {
#             'cctv_a': connectable_tracklet[0][1], 
#             'tracklet_a': connectable_tracklet[0][2], 
#             'cctv_b': connectable_tracklet[1][1], 
#             'tracklet_b': connectable_tracklet[1][2], 
#         }
#     else:
#         data = {
#             'cctv_a': connectable_tracklet[1][1], 
#             'tracklet_a': connectable_tracklet[1][2], 
#             'cctv_b': connectable_tracklet[0][1], 
#             'tracklet_b': connectable_tracklet[0][2], 
#         }
    

#     max_id = 'SELECT max(trajectory_id) FROM exit_entry_link'
#     cur.execute(max_id)
#     max_trajectory_id = cur.fetchone()[0]

#     print(max_trajectory_id)
    
#     cur.execute(sql, data)
#     result = cur.fetchone()

#     if result is not None: 
#         trajectory = result
#     else:
#         if max_trajectory_id is None:
#             trajectory = 1
#         else:
#             trajectory = max_trajectory_id + 1
            
            
#     sql = '''
#     UPDATE exit_entry_link SET trajectory_id=%(trajectory_id)s AND score=%(score)s 
#     WHERE cctv_a_id=%(cctv_a_id)s AND tracklet_b_id=%(tracklet_a_id)s AND cctv_b_id=%(cctv_b_id)s AND tracklet_b_id=%(tracklet_b_id)s
#     '''

#     if connectable_tracklet[0][1] < connectable_tracklet[1][1]:
#         data = {
#             'trajectory_id': trajectory, 
#             'cctv_a_id': connectable_tracklet[0][1], 
#             'tracklet_a_id': connectable_tracklet[0][2], 
#             'cctv_b_id': connectable_tracklet[1][1], 
#             'tracklet_b_id': connectable_tracklet[1][2], 
#             'score': score,
#         }
#     else:
#         data = {
#             'trajectory_id': trajectory, 
#             'cctv_a_id': connectable_tracklet[1][1], 
#             'tracklet_a_id': connectable_tracklet[1][2], 
#             'cctv_b_id': connectable_tracklet[0][1], 
#             'tracklet_b_id': connectable_tracklet[0][2], 
#             'score': score,
#         }

#     cur.execute(sql, data)
#     conn.commit()








def connet_tracklet(connectable_tracklet, score):
    sql = '''
    SELECT trajectory_id FROM trajectory 
    WHERE (cctv_a_id=%(cctv_a)s AND tracklet_a_id=%(tracklet_a)s)
        OR (cctv_b_id=%(cctv_b)s AND tracklet_b_id=%(tracklet_b)s)
        OR (cctv_a_id=%(cctv_b)s AND tracklet_a_id=%(tracklet_b)s)
        OR (cctv_b_id=%(cctv_a)s AND tracklet_b_id=%(tracklet_a)s)
    '''
    if connectable_tracklet[0][1] < connectable_tracklet[1][1]:
        data = {
            'cctv_a': connectable_tracklet[0][1], 
            'tracklet_a': connectable_tracklet[0][2], 
            'cctv_b': connectable_tracklet[1][1], 
            'tracklet_b': connectable_tracklet[1][2], 
        }
    else:
        data = {
            'cctv_a': connectable_tracklet[1][1], 
            'tracklet_a': connectable_tracklet[1][2], 
            'cctv_b': connectable_tracklet[0][1], 
            'tracklet_b': connectable_tracklet[0][2], 
        }
    

    max_id = 'SELECT max(trajectory_id) FROM trajectory'
    cur.execute(max_id)
    max_trajectory_id = cur.fetchone()[0]

    print(max_trajectory_id)
    
    cur.execute(sql, data)
    result = cur.fetchone()

    if result is not None: 
        trajectory = result[0]
    else:
        if max_trajectory_id is None:
            trajectory = 1
        else:
            trajectory = max_trajectory_id + 1
            
            
    sql = '''
    UPDATE trajectory SET trajectory_id=%(trajectory_id)s, score=%(score)s 
    WHERE cctv_a_id=%(cctv_a_id)s AND tracklet_b_id=%(tracklet_a_id)s AND cctv_b_id=%(cctv_b_id)s AND tracklet_b_id=%(tracklet_b_id)s
    '''

    if connectable_tracklet[0][1] < connectable_tracklet[1][1]:
        data = {
            'trajectory_id': trajectory, 
            'cctv_a_id': connectable_tracklet[0][1], 
            'tracklet_a_id': connectable_tracklet[0][2], 
            'cctv_b_id': connectable_tracklet[1][1], 
            'tracklet_b_id': connectable_tracklet[1][2], 
            'score': score,
        }
    else:
        data = {
            'trajectory_id': trajectory, 
            'cctv_a_id': connectable_tracklet[1][1], 
            'tracklet_a_id': connectable_tracklet[1][2], 
            'cctv_b_id': connectable_tracklet[0][1], 
            'tracklet_b_id': connectable_tracklet[0][2], 
            'score': score,
        }

    cur.execute(sql, data)
    conn.commit()







def get_final_score(speed_rate, size_rate, grid_score, candidate):
    # grid score
    final_score = grid_score
    
    # rate = b / a
    if candidate[0][1] < candidate[1][1]:
        a = candidate[0]
        b = candidate[1]
    else:
        a = candidate[1]
        b = candidate[0]

    # size
    estimated_size = a[4] * size_rate
    final_score *= 1 - (abs(estimated_size - b[4]) / b[4])
    
    # # speed
    # estimated_speed = a[5] * speed_rate
    # final_score *= 1 - (abs(estimated_speed - b[5]) / b[5])

    return final_score



def main():
    start()
    with open('../logs/logmerger/1111/500_2/monitoring/new_output.txt') as r:
        lines = r.readlines()
        for line in lines:
            algorithm(line)
    finish()

main()