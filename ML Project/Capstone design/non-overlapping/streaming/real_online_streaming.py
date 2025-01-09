import psycopg2

##############
# log schema #
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
    global true_link

    entry_log_buffer = []
    exit_log_buffer = []
    buffer = dict()
    candidates = dict()
    true_link = list()

    # conn = psycopg2.connect(host="localhost", database="mct", user="mct", password="password")
    conn = psycopg2.connect(host="localhost", database="mct_streaming", user="mct", password="password")
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
 

def get_grid_score(cctv_a, grid_a, cctv_b, grid_b):
    sql = '''
    SELECT T.cnt/B.cnt AS rate
    FROM
        (SELECT cctv_a_id, grid_a_id, sum(count) AS cnt
        FROM grid_mapping_table
        GROUP BY (cctv_a_id, grid_a_id)) AS B,
        (SELECT cctv_a_id, grid_a_id, cctv_b_id, grid_b_id, count AS cnt
        FROM grid_mapping_table
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

    if result is None:
        return 0
    else:
        return float(result[0])


def get_the_size_and_speed_variation_rate(cctv_a, grid_a, cctv_b, grid_b):
    sql = '''
    SELECT speed_variation_rate, size_variation_rate FROM grid_mapping_table
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

    if result is None:
        return (0, 0)
    else:
        return result


def get_connected_cctv_list(cctv_id):
    sql = '''
    SELECT cctv_a_id AS cctv_id FROM link_init WHERE cctv_b_id=%(cctv_id)s
    UNION
    SELECT cctv_b_id AS cctv_id FROM link_init WHERE cctv_a_id=%(cctv_id)s
    '''
    data = {
        'cctv_id': cctv_id,
    }
    cur.execute(sql, data)
    results = cur.fetchall()
    
    return results


def get_timegaps(cctv_a, grid_a, cctv_b, grid_b):
    sql = '''
    SELECT time_lower_bound, time_upper_bound FROM grid_mapping_table
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

    if result is None:
        return (0, 0)
    else:
        return result


def get_final_score(speed_rate, size_rate, grid_score, exit_log, entry_log):
    # grid score
    final_score = grid_score
    
    # rate = b / a
    if exit_log[1] < entry_log[1]:
        a = exit_log
        b = entry_log
    else:
        a = entry_log
        b = exit_log

    # size
    estimated_size = a[4] * size_rate
    final_score *= 1 - (abs(estimated_size - b[4]) / b[4])
    
    # speed, for now, is not so accurate to use
    # speed
    # estimated_speed = a[5] * speed_rate
    # final_score *= 1 - (abs(estimated_speed - b[5]) / b[5])

    return final_score




def algorithm(line):
    unit_time = 1_000

    segmented_log = line.split('\t')
    
    # segmented_log[0]
    # 1: human
    # 100: head
    if segmented_log[1] == '1':

        key = (segmented_log[2], segmented_log[0]) # buffer_key = (cctv_id, tracklet_id)

        grids = list(map(int, segmented_log[4].split(',')))
        sizes = list(map(float, segmented_log[5].split(',')))
        speeds = list(map(float, segmented_log[9].split(',')))

        log = ([segmented_log[3],], segmented_log[2], segmented_log[0], grids, sizes, speeds)
        

        ##########################
        ##########################
        # INSERT THE EXIT LOG
        ##########################
        ##########################

        # insert new 'exit log'
        # if the value of speed is -1, because of the default setting,
        # find the earlier one and check whether it's -1 and if so, do the same thing again
        for buffer_log in buffer.values():
            # compares the current_time (segmented_log[3]) to buffer_log timestamp
            if (int(segmented_log[3]) - int(buffer_log[0][-1])) > unit_time:
                buffer.pop( (buffer_log[1], buffer_log[2]) )
                if buffer_log[5][-1] == -1:
                    if buffer_log[5][len(buffer_log[5])-2] == -1:
                        speed = buffer_log[5][len(buffer_log[5])-3]
                    else:   
                        speed = buffer_log[5][len(buffer_log[5])-2]
                else:
                    speed = buffer_log[5][-1]

                exit_log = (int(buffer_log[0][-1])+500, int(buffer_log[1]), int(buffer_log[2]), buffer_log[3][-1], buffer_log[4][-1], speed)

                exit_log_buffer.append(exit_log)
                push_the_raw_log(exit_log, 'exit')
                break # is neccesary?
        

        ##########################
        ##########################
        # INSERT THE ENTRY LOG AND UPDATE THE LOG
        ##########################
        ##########################

        # if the key, (cctv_id, tracklet_id), is not in the buffer's keylist
        # insert new 'entry log'
        if key not in buffer.keys():
            entry_log = (int(segmented_log[3]), int(segmented_log[2]), int(segmented_log[0]), grids[0], sizes[0], speeds[0])

            buffer[key] = log

            entry_log_buffer.append(entry_log)
            push_the_raw_log(entry_log, 'entry')
        
        # unless
        # update the 'existing log'
        else:
            timestamp, cctv_id, tracklet_id, grid_list, size_list, speed_list = buffer[key]
            timestamp.extend(log[0])
            grid_list.extend(log[3])
            size_list.extend(log[4])
            speed_list.extend(log[5])
            updated_log = (timestamp, cctv_id, tracklet_id, grid_list, size_list, speed_list)
            buffer[key] = updated_log  
        
        if len(exit_log_buffer) > 0:
            make_candidates(exit_log_buffer, entry_log_buffer, log[0])


##########################
# LINK THE LINKABLE LOGS
##########################
def make_candidates(exit_log_buffer, entry_log_buffer, current_log):
    wait_for_evaluation = 1_000

    for exit_log in exit_log_buffer:
        for entry_log in entry_log_buffer:
            print("true_link", true_link)
            print("pair", (exit_log[1], exit_log[2], entry_log[1], entry_log[2]) )
            if (exit_log[1], exit_log[2], entry_log[1], entry_log[2]) in true_link:
                try:
                    exit_log_buffer.remove(exit_log)
                    entry_log_buffer.remove(entry_log)
                except:
                    pass
                break

            cctv_list = get_connected_cctv_list(exit_log[1])
            # can make it return True or False
            if (entry_log[1],) in cctv_list:
                # if there's no timegap information in the mapping table for given logs, ignore them
                # if the timegap is None, get_timegaps() will return (0, 0), so that nothing can be met
                lower_bound, upper_bound = get_timegaps(entry_log[1], entry_log[3], exit_log[1], exit_log[3])
                # print(lower_bound, upper_bound, entry_log[0]-exit_log[0])
                
                if (lower_bound <= (entry_log[0] - exit_log[0]) <= upper_bound):
                    speed_rate, size_rate = get_the_size_and_speed_variation_rate(exit_log[1], exit_log[3], entry_log[1], entry_log[3])
                    grid_score = get_grid_score(exit_log[1], exit_log[3], entry_log[1], entry_log[3])
                    final_score = get_final_score(speed_rate, size_rate, grid_score, exit_log, entry_log)

                    # print(final_score)

                    if final_score == 0:
                        pass
                    elif exit_log in candidates.values():
                        if entry_log not in candidates[exit_log]:
                            candidate_value = candidates[exit_log]
                            candidate_value.extend( (entry_log, final_score) )
                            candidates[exit_log] = candidate_value
                    else:
                        candidates[exit_log] = [(entry_log, final_score),]
        
         # candidate->entry->timestamp + 500ms
        if (exit_log in candidates.keys()) and (int(current_log[-1]) > candidates[exit_log][0][0][0] + wait_for_evaluation):
            evalute_candidate(candidates, exit_log)            
            result = (exit_log, candidates[exit_log][0], candidates[exit_log][1])
            connet_tracklet((result[0], result[1]), result[2])

            exit_log_buffer.remove(exit_log)
            entry_log_buffer.remove(candidates[exit_log][0])

            true_link.append((exit_log[1], exit_log[2], candidates[exit_log][0][1], candidates[exit_log][0][2]))
            candidates.pop(exit_log)


#####################################
# evaluate the candidate dictionary #
#####################################

def evalute_candidate(candidates, candidate_key):
    # for candidate_key in candidates.keys():
    max_score = 0
    connected_value = []
    for candidate_value in candidates[candidate_key]:
        if max_score < candidate_value[1]:
            max_score = candidate_value[1]
            connected_value = candidate_value
    candidates[candidate_key] = connected_value



##########################
# update exit_entry_link #
##########################

def connet_tracklet(connectable_tracklet, score):
    sql = '''
    SELECT trajectory_id FROM exit_entry_link 
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
    
    cur.execute(sql, data)
    result = cur.fetchone()

    if result is not None: 
        trajectory = result
    else:
        max_id = 'SELECT max(trajectory_id) FROM exit_entry_link'
        cur.execute(max_id)
        max_trajectory_id = cur.fetchone()[0]

        if max_trajectory_id is None:
            trajectory = 1
        else:
            trajectory = max_trajectory_id + 1
            

    sql_insert = '''
    INSERT INTO exit_entry_link VALUES (
        %(timestamp_a)s, %(cctv_a)s, %(grid_a)s, %(tracklet_a)s, %(speed_a)s, %(size_a)s,
        %(timestamp_b)s, %(cctv_b)s, %(grid_b)s, %(tracklet_b)s, %(speed_b)s, %(size_b)s,
        %(trajectory_id)s, %(score)s)
    '''
    if connectable_tracklet[0][1] < connectable_tracklet[1][1]:
        data = {
            'trajectory_id': trajectory, 
            'timestamp_a': connectable_tracklet[0][0],
            'cctv_a': connectable_tracklet[0][1], 
            'tracklet_a': connectable_tracklet[0][2], 
            'grid_a': connectable_tracklet[0][3],
            'speed_a': connectable_tracklet[0][5],
            'size_a': connectable_tracklet[0][4],
            'timestamp_b': connectable_tracklet[1][0],
            'cctv_b': connectable_tracklet[1][1], 
            'tracklet_b': connectable_tracklet[1][2], 
            'grid_b': connectable_tracklet[1][3],
            'speed_b': connectable_tracklet[1][5],
            'size_b': connectable_tracklet[1][4],
            'score': score,
        }
    else:
        data = {
            'trajectory_id': trajectory, 
            'timestamp_a': connectable_tracklet[0][0],
            'cctv_a': connectable_tracklet[1][1], 
            'tracklet_a': connectable_tracklet[1][2], 
            'grid_a': connectable_tracklet[1][3],
            'speed_a': connectable_tracklet[1][5],
            'size_a': connectable_tracklet[1][4],
            'timestamp_b': connectable_tracklet[1][0],
            'cctv_b': connectable_tracklet[0][1], 
            'tracklet_b': connectable_tracklet[0][2], 
            'grid_b': connectable_tracklet[0][3],
            'speed_b': connectable_tracklet[0][5],
            'size_b': connectable_tracklet[0][4],
            'score': score,
        }

    cur.execute(sql_insert, data)
    conn.commit()


def main():
    start()
    with open('../logs/final/learning_output.txt') as r:
        lines = r.readlines()
        for line in lines:
            algorithm(line)
    finish()

main()