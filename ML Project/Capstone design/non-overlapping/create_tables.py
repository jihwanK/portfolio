import psycopg2

conn = psycopg2.connect(host="localhost", database="mct", user="mct", password="password")
cur = conn.cursor()

create_exit_entry_link = '''
create table exit_entry_link
(
  timestamp_a   bigint  not null,
  cctv_a_id     bigint  not null,
  grid_a_id     integer not null,
  tracklet_a_id bigint  not null,
  speed_a       bigint  not null,
  size_a        bigint  not null,
  timestamp_b   bigint  not null,
  cctv_b_id     bigint  not null,
  grid_b_id     integer not null,
  tracklet_b_id bigint  not null,
  speed_b       bigint  not null,
  size_b        bigint  not null,
  trajectory_id bigint,
  score         double precision,
  constraint exit_entry_link_pk
  primary key (timestamp_a, cctv_a_id, tracklet_a_id, timestamp_b, cctv_b_id, tracklet_b_id)
)
'''

create_exit_entry_log = '''
create table exit_entry_log
(
  timestamp   bigint           not null,
  cctv_id     bigint           not null,
  tracklet_id bigint           not null,
  grid_id     integer          not null,
  speed       double precision not null,
  size        double precision not null,
  exit_entry  varchar(5)       not null,
  constraint exit_entry_log_pk
  primary key (timestamp, cctv_id, tracklet_id, grid_id)
)
'''

grid_mapping = '''
create table grid_mapping_table
(
  cctv_a_id            bigint  not null,
  grid_a_id            integer not null,
  cctv_b_id            bigint  not null,
  grid_b_id            integer not null,
  time_lower_bound     bigint,
  time_upper_bound     bigint,
  speed_variation_rate double precision,
  size_variation_rate  double precision,
  timegap_avg          double precision,
  timegap_std          double precision,
  count                bigint  not null,
  constraint grid_mapping_table_pk
  primary key (cctv_a_id, grid_a_id, cctv_b_id, grid_b_id)
)
'''

learning_exit_entry_log = '''
create table learning_exit_entry_log
(
  timestamp   bigint           not null,
  cctv_id     bigint           not null,
  tracklet_id bigint           not null,
  grid_id     integer          not null,
  speed       double precision not null,
  size        double precision not null,
  exit_entry  varchar(5)       not null,
  constraint learning_exit_entry_log_pk
  primary key (timestamp, cctv_id, tracklet_id, grid_id)
)
'''

link_init = '''
create table link_init
(
  cctv_a_id        bigint not null,
  cctv_b_id        bigint not null,
  time_lower_bound bigint not null,
  time_upper_bound bigint not null,
  constraint link_init_pk
  primary key (cctv_a_id, cctv_b_id)
)
'''


create_sql = (
  create_exit_entry_link,
  create_exit_entry_log,
  grid_mapping,
  learning_exit_entry_log,
  link_init,
)

for sql in create_sql:
    try:
        cur.execute(sql)
    except psycopg2.ProgrammingError as err:
        print(err)

conn.commit()

cur.close()
conn.close()