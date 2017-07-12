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
    cur.execute("""SELECT location_road, location_area, timestamp, traffic FROM entries WHERE ((location_road = 'EDSA' AND location_area = 'MALL_OF_ASIA') OR (location_road = 'C5' AND location_area = 'ATENEO_DE_MANILA_UNIVERSITY') OR (location_road = 'ORTIGAS' AND location_area = 'LA_SALLE_GREENHILLS')) AND timestamp LIKE '%Wed%' AND timestamp LIKE '%2017%'""")
except:
    print("Data retrieval failed.")

data = cur.fetchall()
for row in data:
    print(row)
