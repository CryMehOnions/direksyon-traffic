import psycopg2

print("Attempting to connect...")
try:
    conn = psycopg2.connect("host='128.199.106.13' dbname='mmda_traffic' user='direksyon' host='localhost' password='gothere4lyf'")
    print("Connection successful")
except:
    print("DB connect failed.")

cur = conn.cursor()

    # check when last update was
    #

print("Querying database...")
try:
    cur.execute("""SELECT timestamp FROM entries WHERE update_timestamp > timestamp '2017-07-01 00:00:00' ORDER BY timestamp""")
except:
    print("Data retrieval failed.")

data = cur.fetchall()
for row in data:
    print(row)
