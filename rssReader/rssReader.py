#!/usr/bin/python

import psycopg2
import feedparser

feedURL = "http://mmdatraffic.interaksyon.com/livefeed/"
dataDict = feedparser.parse(feedURL)
dataDict = dataDict.entries
print "Feed Retrieval Successful"

entryList = []

for data in dataDict:
	guid = data['guid'].split('/')[4]
	title = data.title.split('-')

	road = title[0]
	bound = title[-1]
	title.remove(road)
	title.remove(bound)
	area = "-".join(title)

	entry = {'location_road' : road, 'location_area' : area, 'location_bound' : bound, 'traffic' : data.description, 'guid' : int(guid), 'timestamp' : data.published}
	entryList.append(entry)

try:
	conn = psycopg2.connect("dbname='mmda_traffic' user='direksyon' host='localhost' password='gothere4lyf'")
	print "Connection Successful"
except:
	print "Cannot connect to database"

insertQuery = """INSERT INTO entries (location_road, location_area, location_bound, traffic, guid, timestamp) VALUES (%(location_road)s, %(location_area)s, %(location_bound)s, %(traffic)s, %(guid)s, %(timestamp)s) ON CONFLICT(guid) DO NOTHING"""

cur = conn.cursor()
cur.executemany(insertQuery, tuple(entryList))

conn.commit()
conn.close()
