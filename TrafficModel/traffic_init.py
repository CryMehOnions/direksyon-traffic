import psycopg2

# DB Connect
def initialize_tree():
    try:
        conn = psycopg2.connect("dbname='mydb' user='postgres' host='localhost' password='password'")
    except:
        print("DB connect failed.")

    cur = conn.cursor()

    try:
        cur.execute("""SELECT location_road, location_bound, location_area, timestamp, traffic FROM mmda_traffic""")
    except:
        print("Data retrieval failed.")

    data = cur.fetchall()

    for row in data:  # Street, Day of Week, Time Interval, Traffic Condition
        # combines location elements
        row[0:2] = ['-'.join(row[0:2])]

        # splits timestamp into day and time interval
        timestamp = row[1].split(
            ' ')  # timestamp[0] = Day of Week, timestamp[1] = Day, timestamp[2] = Month, timestamp[3] = Year, timestamp[4] = Time

        # delete not needed time information (timestamp[0] = Day of Week, timestamp[1] = Time)
        timestamp.
        del (timestamp[3])  # deletes year
        timestamp.
        del (timestamp[2])  # deletes month
        timestamp.
        del (timestamp[1])  # deletes day
        timestamp[0] = timestamp[0].replace(',', '')

        # convert time to interval value
        time = timestamp[1].split(':')
        timestamp[1] = ((int(time[0]) * 60) + int(time[1])) / 15

        # adds new time elements into row
        row.
        del (1)
        row.extend(timestamp)

        # Result: row[0] = Street, row[1] = Day of Week, row[2] = Time Interval
