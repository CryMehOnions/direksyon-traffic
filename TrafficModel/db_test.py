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
    cur.execute("""SELECT location_road, location_area, location_bound, timestamp, traffic FROM entries WHERE (location_road = 'C5' AND location_area = 'ATENEO_DE_MANILA_UNIVERSITY') AND timestamp LIKE '%Tue%' AND (timestamp LIKE '%2017%' OR (timestamp LIKE '%2016%' AND timestamp LIKE '%Dec%')) AND timestamp NOT LIKE '% 14: %' AND timestamp NOT LIKE '% 15:%'""")
except:
    print("Data retrieval failed.")

data = cur.fetchall()
for row in data:
    print(row)
