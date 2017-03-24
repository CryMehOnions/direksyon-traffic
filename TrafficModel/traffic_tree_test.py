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

    new_row = list(row)
    print("Raw row as list: ")
    print(new_row)

    # combines location elements
    new_row[0] = '-'.join(new_row[0::2]) # 0 - Street, 1 - timestamp, 2 - traffic

    del new_row[1]
    del new_row[1]

    # splits timestamp into day and time interval
    timestamp = new_row[1].split(' ')
    # timestamp[0] = Day of Week, timestamp[1] = Day, timestamp[2] = Month, timestamp[3] = Year, timestamp[4] = Time


    # delete not needed time information (timestamp[0] = Day of Week, timestamp[1] = Time)
    del timestamp[1]  # deletes year
    del timestamp[1]  # deletes month
    del timestamp[1]  # deletes day
    del timestamp[2]  # deletes last thing

    timestamp[0] = timestamp[0].replace(',', '')

    # convert time to interval value
    day_of_week = timestamp[0]
    split_stamp = timestamp[1].split(':')
    interval = ((int(split_stamp[0]) * 60) + int(split_stamp[1])) / 15

    traffic_con = new_row[2]

    # adds new time elements into row
    del new_row[1]
    del new_row[1]

    new_row.append(day_of_week)
    new_row.append(interval)
    new_row.append(traffic_con)

    row = tuple(new_row)

    # Result: row[0] = Street, row[1] = Day of Week, row[2] = Time Interval

    print("After conversion: ")
    print(row)

    print("\n\n")
