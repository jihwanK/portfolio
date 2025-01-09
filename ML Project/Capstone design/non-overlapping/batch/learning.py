import psycopg2

# offline learning

# with open('output.tsv', 'r') as ostream:
#     output = ostream.readlines()
#     for line in output:
#         tracklet_id, cctv_id, timestamp, grid_list, avg_size_grid, std_size_grid, avg_speed_grid, std_speed_grid = line.split()


def push_raw_to_entry_exit_log(fname):
    ostream = open(fname, 'r')
    lines = ostream.readlines()

    prev_tracklet_id = -99
    prev_speeds_avg = [0,0]

    for line in lines:
        tracklet_id, cctv_id, timestamp, grid_list, avg_size_by_grid, std_size_by_grid, avg_speed_by_grid, std_speed_by_grid = line.split()
        
        passed_grids = grid_list.split(',')
        speeds_avg = avg_speed_by_grid.split(',')
        sizes_avg = avg_size_by_grid.split(',')

        sql = '''
        INSERT INTO EXIT_ENTRY_LOG (timestamp, cctv_id, tracklet_id, grid_id, speed, size, exit_entry)
        VALUES
        (%(timestamp)s, %(cctv_id)s, %(tracklet_id)s, %(grid_id)s, %(speed)s, %(size)s, %(exit_entry)s)'''

        if prev_tracklet_id != tracklet_id:
            ######################
            # for the last frame #
            ######################
            if int(prev_tracklet_id) > 0:  

                # if the speed from the parser comes out to be -1
                # we will choose the second to last one 
                if float(prev_speeds_avg[-1]) < 0 and len(prev_speeds_avg) == 1:
                    exit_speed = prev_prev_speeds_avg[-1]
                elif float(prev_speeds_avg[-1]) < 0 and len(prev_speeds_avg) > 1:
                    exit_speed = prev_speeds_avg[len(prev_speeds_avg)-2]
                elif float(prev_speeds_avg[-1]) < 0 and prev_prev_tracklet_id != prev_tracklet_id:
                    exit_speed = prev_speeds_avg[len(prev_speeds_avg)-2]
                else:
                    exit_speed = prev_speeds_avg[-1]

                exit_timestamp = int(prev_timestamp) + 500
                exit_grid = prev_passed_grids[-1]
                # exit_speed = prev_speeds_avg[-1]
                exit_size = prev_sizes_avg[-1]
                
                exit_data = {
                    'timestamp': exit_timestamp,
                    'cctv_id': prev_cctv_id,
                    'tracklet_id': prev_tracklet_id,
                    'grid_id': exit_grid,
                    'speed': exit_speed,
                    'size': exit_size,
                    'exit_entry': 'exit',
                }
                cur.execute(sql, exit_data)

            #######################
            # for the first frame #
            #######################
            entry_timestamp = timestamp
            entry_grid = passed_grids[0]
            entry_speed = speeds_avg[0]
            entry_size = sizes_avg[0]

            entry_data = {
                'timestamp': entry_timestamp,
                'cctv_id': cctv_id,
                'tracklet_id': tracklet_id,
                'grid_id': entry_grid,
                'speed': entry_speed,
                'size': entry_size,
                'exit_entry': 'entry',
            }
            cur.execute(sql, entry_data)

        prev_prev_speeds_avg = prev_speeds_avg
        prev_prev_tracklet_id = prev_tracklet_id

        prev_tracklet_id = tracklet_id
        prev_cctv_id = cctv_id
        prev_timestamp = timestamp
        prev_passed_grids = passed_grids
        prev_speeds_avg = speeds_avg
        prev_sizes_avg = sizes_avg

    conn.commit()



# need to convert push_to_link() into [one single SQL]

def push_to_link_sql():
    # join the table on cctv_id which is linking; can get this info from LINK_INIT
    linked_cctv_info_sql = 'SELECT * FROM LINK_INIT'
    cur.execute(linked_cctv_info_sql)
    linked_cctv_infos = cur.fetchall()

    for linked_cctv_info in linked_cctv_infos:
        sql = '''
        INSERT INTO LINK (log_a_id, log_b_id, timegap)
        SELECT cctv_a.log_id, cctv_b.log_id, abs(cctv_a.timestamp-cctv_b.timestamp)
        FROM EXIT_ENTRY_LOG AS cctv_a
            INNER JOIN EXIT_ENTRY_LOG AS cctv_b ON (cctv_a.cctv_id=%(cctv_a_id)s AND cctv_b.cctv_id=%(cctv_b_id)s)
        WHERE
            (abs(cctv_a.timestamp-cctv_b.timestamp) <= 5500) AND 
            (
                (cctv_a.exit_entry='entry' AND cctv_b.exit_entry='exit' AND cctv_a.timestamp > cctv_b.timestamp) OR 
                (cctv_b.exit_entry='entry' AND cctv_a.exit_entry='exit' AND cctv_a.timestamp < cctv_b.timestamp)
            )
        '''

        data = {
            'cctv_a_id': linked_cctv_info[0],
            'cctv_b_id': linked_cctv_info[1],
        }
        
        cur.execute(sql, data)

    conn.commit()





def push_to_link():
    fetch_exit_log = 'SELECT * FROM EXIT_ENTRY_LOG WHERE exit_entry=\'exit\' ORDER BY timestamp'
    cur.execute(fetch_exit_log)
    exits = cur.fetchall() # returns list of tuples
    
    fetch_entry_log = 'SELECT * FROM EXIT_ENTRY_LOG WHERE exit_entry=\'entry\' ORDER BY timestamp'
    cur.execute(fetch_entry_log)
    entries = cur.fetchall()

    for exit_line in exits:
        connected_cctv_info = 'SELECT * FROM LINK_INIT WHERE cctv_a_id=%(cctv)s OR cctv_b_id=%(cctv)s'
        cctv = {
            'cctv': exit_line[2],
        }
        cur.execute(connected_cctv_info, cctv)
        link_inits = cur.fetchall()

        for link_init in link_inits:
            # exit_line[2] -> cctv_id
            if link_init[0] == exit_line[2]:
                # check link_init[0] (cctv_a) whether it's within time boundary (link_init[2], link_init[3])
                # link_init[2] -> lower_boundary
                # link_init[3] -> upper_boundary
                for entry_line in entries:
                    if (link_init[1] == entry_line[2]) and (link_init[2] <= (entry_line[1] - exit_line[1]) <= link_init[3]):
                        # valid link
                        insert_sql = 'INSERT INTO LINK VALUES (%(log_a_id)s, %(log_b_id)s, %(timegap)s)'
                        if entry_line[0] < exit_line[0]:
                            insert_data = {
                                'timegap': entry_line[1] - exit_line[1],
                                'log_a_id': entry_line[0],
                                'log_b_id': exit_line[0],
                            }
                        else:
                            insert_data = {
                                'timegap': entry_line[1] - exit_line[1],
                                'log_a_id': exit_line[0],
                                'log_b_id': entry_line[0],
                            }
                        cur.execute(insert_sql, insert_data)
            elif link_init[1] == exit_line[2]:
                # check link_init[1] (cctv_b) whether it's within time boundary (link_init[2], link_init[3])
                for entry_line in entries:
                    if (link_init[0] == entry_line[2]) and (link_init[2] <= (entry_line[1] - exit_line[1]) <= link_init[3]):
                        # valid link
                        insert_sql = 'INSERT INTO LINK VALUES (%(log_a_id)s, %(log_b_id)s, %(timegap)s)'
                        if entry_line[0] < exit_line[0]:
                            insert_data = {
                                'timegap': entry_line[1] - exit_line[1],
                                'log_a_id': entry_line[0],
                                'log_b_id': exit_line[0],
                            }
                        else:
                            insert_data = {
                                'timegap': entry_line[1] - exit_line[1],
                                'log_a_id': exit_line[0],
                                'log_b_id': entry_line[0],
                            }
                        cur.execute(insert_sql, insert_data)
    conn.commit()


def push_link_info_sql():
    sql = '''
    INSERT INTO LINK_INFO (cctv_a_id, grid_a_id, cctv_b_id, grid_b_id,
        time_lower_bound, time_upper_bound, timegap_avg, timegap_std, count,
        speed_variation_rate, size_variation_rate)
    SELECT *
    FROM
        (SELECT s1.cctv_a_id, s1.grid_a_id, s1.cctv_b_id, s1.grid_b_id,
        (s1.timegap_avg-s1.timegap_std), (s1.timegap_avg+s1.timegap_std), s1.timegap_avg, s1.timegap_std, cnt,
        GREATEST(0, s3.speed_avg/s2.speed_avg), s3.size_avg/s2.size_avg
          FROM GRID_INFO AS s2
                   INNER JOIN
        (SELECT e1.cctv_id AS cctv_a_id, e1.grid_id AS grid_a_id, e2.cctv_id AS cctv_b_id, e2.grid_id AS grid_b_id,
        avg(abs(e1.timestamp-e2.timestamp)) AS timegap_avg, COALESCE(stddev(abs(e1.timestamp-e2.timestamp)), 0) AS timegap_std, count(*) AS cnt
        FROM ((LINK
            INNER JOIN EXIT_ENTRY_LOG AS e1 ON LINK.log_a_id = e1.log_id)
            INNER JOIN EXIT_ENTRY_LOG AS e2 ON LINK.log_b_id = e2.log_id)
        GROUP BY e1.cctv_id, e1.grid_id, e2.cctv_id, e2.grid_id) AS s1
                    ON s2.cctv_id=s1.cctv_a_id and s2.grid_id=s1.grid_a_id
            INNER JOIN GRID_INFO AS s3 ON s3.cctv_id=s1.cctv_b_id and s3.grid_id=s1.grid_b_id) AS r
    '''
    cur.execute(sql)
    conn.commit()




def push_link_info():
    link_info_sql = '''
    SELECT e1.cctv_id, e1.grid_id, e2.cctv_id, e2.grid_id,
    avg(abs(e1.timestamp-e2.timestamp)), stddev(abs(e1.timestamp-e2.timestamp)), count(*)
    FROM ((LINK
    INNER JOIN EXIT_ENTRY_LOG AS e1 ON LINK.log_a_id = e1.log_id)
    INNER JOIN EXIT_ENTRY_LOG AS e2 ON LINK.log_b_id = e2.log_id)
    GROUP BY e1.cctv_id, e1.grid_id, e2.cctv_id, e2.grid_id'''
    cur.execute(link_info_sql)
    infos = cur.fetchall()

    for info in infos:
        push_sql = '''
        INSERT INTO LINK_INFO (cctv_a_id, grid_a_id, cctv_b_id, grid_b_id,
        time_lower_bound, time_upper_bound, timegap_avg, timegap_std, count, 
        speed_variation_rate, size_variation_rate)
        VALUES (%(cctv_a_id)s, %(grid_a_id)s, %(cctv_b_id)s, %(grid_b_id)s, 
        %(time_lower_bound)s, %(time_upper_bound)s, %(timegap_avg)s, %(timegap_std)s, %(count)s, 
        %(speed_variation_rate)s, %(size_variation_rate)s)'''

        if info[5] == 0:
            std = 500
        elif info[5] is None:
            std = 500
        else:
            std = info[5]

        grid_info = 'SELECT size_avg, speed_avg FROM GRID_INFO WHERE cctv_id=%(cctv_id)s and grid_id=%(grid_id)s'
        data_ca = {
            'cctv_id': info[0],
            'grid_id': info[1],
        }
        data_cb = {
            'cctv_id': info[2],
            'grid_id': info[3],
        }

        cur.execute(grid_info, data_ca)
        avg_ca = cur.fetchone()
        cur.execute(grid_info, data_cb)
        avg_cb = cur.fetchone()
        size_rate = avg_cb[0] / avg_ca[0]
        
        # if the value of the speed is -1, set the speed_rate to -1 to make sure it is anomaly
        if avg_ca[1] == -1 or avg_cb[1] == -1:
            speed_rate = -1
        else:
            speed_rate = avg_cb[1] / avg_ca[1]

        push_data = {
            'cctv_a_id': info[0],
            'grid_a_id': info[1],
            'cctv_b_id': info[2],
            'grid_b_id': info[3],
            'time_lower_bound': float(info[4]) - 2*float(std), 
            'time_upper_bound': float(info[4]) + 2*float(std), 
            'timegap_avg': info[4], 
            'timegap_std': std,
            'count': info[6],
            'speed_variation_rate': speed_rate,
            'size_variation_rate': size_rate,
        }

        cur.execute(push_sql, push_data)
    conn.commit()


def push_grid_info():
    # only for valid link
    grid_info_sql = '''
    INSERT INTO GRID_INFO (cctv_id, grid_id, size_avg, size_std, speed_avg, speed_std, count) 
    SELECT e.cctv_id, e.grid_id, avg(e.size), COALESCE(stddev(e.size), 0), avg(e.speed), COALESCE(stddev(e.speed), 0), count(*)
    FROM LINK AS l INNER JOIN EXIT_ENTRY_LOG AS e ON l.log_a_id = e.log_id OR l.log_b_id = e.log_id
    GROUP BY e.cctv_id, e.grid_id'''

    cur.execute(grid_info_sql)
    conn.commit()


def delete_all_table():
    sql = '''
    DELETE FROM EXIT_ENTRY_LOG;
    ALTER SEQUENCE exit_entry_log_log_id_seq RESTART ;

    DELETE FROM LINK_INFO;
    ALTER SEQUENCE link_info_link_info_id_seq RESTART ;

    DELETE FROM GRID_INFO;
    ALTER SEQUENCE grid_info_grid_info_id_seq RESTART ;

    DELETE FROM LINK;'''
    
    cur.execute(sql)
    conn.commit()



def start():
    global conn
    global cur

    conn = psycopg2.connect(host="localhost", database="mct", user="mct", password="password")
    cur = conn.cursor()


    delete_all_table()

    # push_raw_to_entry_exit_log('logs/logmerger/1111/500_2/first/first_cctv1.tsv')
    # push_raw_to_entry_exit_log('logs/logmerger/1111/500_2/first/first_cctv2.tsv')

    # push_raw_to_entry_exit_log('logs/logmerger/1111/500_2/second/second_cctv1.tsv')
    # push_raw_to_entry_exit_log('logs/logmerger/1111/500_2/second/second_cctv2.tsv')

    # push_raw_to_entry_exit_log('logs/logmerger/1111/500_2/third/third_cctv1.tsv')
    # push_raw_to_entry_exit_log('logs/logmerger/1111/500_2/third/third_cctv2.tsv')



    push_raw_to_entry_exit_log('../logs/final/first_cctv1.tsv')
    push_raw_to_entry_exit_log('../logs/final/first_cctv2.tsv')

    # push_to_link()
    push_to_link_sql()

    push_grid_info()

    push_link_info()
    # push_link_info_sql()


    cur.close()
    conn.close()
    



start()


