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
    cur.execute("""SELECT * FROM entries WHERE (location_road = 'ORTIGAS' AND location_area = 'LA_SALLE_GREENHILLS') AND timestamp LIKE '%Sat%' AND (timestamp LIKE '%2017%') AND timestamp NOT LIKE '% 14: %' AND timestamp NOT LIKE '% 15:%'""")
except:
    print("Data retrieval failed.")

data = cur.fetchall()
for row in data:
    print(row)
