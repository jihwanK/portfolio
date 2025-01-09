import mysql.connector

############################
### DATABASE CONNECTION ####
############################
conn = mysql.connector.connect(host="localhost", user="root", passwd="password")
cur = conn.cursor()


cur.close()
conn.close()