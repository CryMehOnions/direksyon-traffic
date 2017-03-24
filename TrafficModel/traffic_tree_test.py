import psycopg2

try:
    conn = psycopg2.connect("host='128.199.106.13' dbname='mmda_traffic' user='direksyon' host='localhost' password='gothere4lyf'")
    print("Connection successful")
except:
    print("DB connect failed.")

cur = conn.cursor()

# check when last update was
#

try:
    cur.execute("""SELECT location_road, location_bound, location_area, timestamp, traffic FROM entries WHERE update_timestamp > timestamp '2017-03-20 00:00:00'""")
except:
    print("Data retrieval failed.")

data = cur.fetchall()

for row in data:  # Street, Day of Week, Time Interval, Traffic Condition

    row_temp = list(row)
    print("Raw row as list: ")
    print(row_temp)

    # combines location elements
    print('-'.join(row_temp[0:2])) # 0 - Street, 1 - timestamp, 2 - traffic

    print("After join: ")
    print(row_temp)

    # splits timestamp into day and time interval
    timestamp = row_temp[1].split(' ')
    # timestamp[0] = Day of Week, timestamp[1] = Day, timestamp[2] = Month, timestamp[3] = Year, timestamp[4] = Time

    print("Timestamp: ")
    print(timestamp)

    # delete not needed time information (timestamp[0] = Day of Week, timestamp[1] = Time)
    del timestamp[3]  # deletes year
    del timestamp[2]  # deletes month
    del timestamp[1]  # deletes day
    timestamp[0] = timestamp[0].replace(',', '')

    # convert time to interval value
    time = timestamp[1].split(':')
    timestamp[1] = ((int(time[0]) * 60) + int(time[1])) / 15

    # adds new time elements into row
    del row_temp[1]
    row_temp.extend(timestamp)

    # Result: row[0] = Street, row[1] = Day of Week, row[2] = Time Interval

    print(row)
