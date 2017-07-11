import psycopg2
import time
import sys
import pickle
from datetime import datetime


ERROR_THRESHOLD = 20


def printtree(tree, indent=''):
    if tree.results != None:
        print("Prediction: ", str(tree.results), "; error_rate: ", str(tree.error))
    else:
        if tree.col == 0:
            col_name = "STREET"
        elif tree.col == 1:
            col_name = "SEGMENT"
        elif tree.col == 2:
            col_name = "DAY OF WEEK"
        elif tree.col == 3:
            col_name = "TIME INTERVAL"
        else:
            col_name = str(tree.col)
        print(col_name + ':'+str(tree.value)+'? ')
        # Print the branches
        print(indent+'T->', end=" ")
        printtree(tree.true_branch, indent + '  ')
        print(indent+'F->', end=" ")
        printtree(tree.false_branch, indent + '  ')

# USE DECISION TREE

def divideset(rows, column, value):
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row:row[column] >= value
    else:
        split_function = lambda row:row[column] == value

    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]

    return set1, set2


# count of possible results
def countunique(rows):
    results = {}
    for row in rows:
        r = row[len(row)-1]
        if r not in results:
            results[r] = 0
        results[r] += 1
    return results


def entropy(rows):
    from math import log
    log2 = lambda x: log(x)/log(2)
    results = countunique(rows)
    ent = 0.0
    for r in results.keys():
        p = float(results[r])/len(rows)
        ent = ent-p * log2(p)
    return ent


class TreeNode:
    def __init__(self, col=-1, value=None, results=None, true_branch=None, false_branch=None, alt_node=None, instances = 0, error=0):
        self.col = col
        self.value = value
        self.results = results
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.alt_node = alt_node
        self.instances = 0
        self.error = 0


def buildtree(rows, scoref=entropy):

    if len(rows) == 0: return TreeNode()
    current_score = scoref(rows)

    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(0, column_count):
        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        for value in column_values.keys():
            (set1, set2) = divideset(rows, col, value)
            p = float(len(set1)) / len(rows)
            gain = current_score - p * scoref(set1) - (1 - p) * scoref(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)

    if best_gain > 0:
        true_branch = buildtree(best_sets[0])
        false_branch = buildtree(best_sets[1])
        return TreeNode(col=best_criteria[0], value=best_criteria[1],
                        true_branch=true_branch, false_branch=false_branch)
    else:
        return TreeNode(results=countunique(rows))


def build_tree_incremental(row, tree):
    if tree.results != None: # tree node is not a leaf node
        pruned = false# check for pruning
        if pruned != true:
            if tree.error > ERROR_THRESHOLD:
                create_alternate_tree(tree)


def classify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        obs = observation[tree.col]
        branch = None
        if isinstance(obs, int) or isinstance(obs, float):
            if obs >= tree.value:
                branch = tree.true_branch
            else:
                branch = tree.false_branch
        else:
            if obs == tree.value:
                branch = tree.true_branch
            else:
                branch = tree.false_branch
        return classify(observation, branch)
		
		
def compare_actual_to_predicted(row, model): # true = match
    if classify([row[0], row[1], row[2], row[3], row[4]], model) == row[5]:
        return true
    else:
        return false
	
	
def update_error_rate(node, is_accurate):
    old_error = node.error
    num_wrong = node.error * node.instances
    node.instances = node.instances + 1
    if is_accurate:
        node.error = num_wrong/node.instances
    else:
        node.error = (num_wrong+1)/node.instances


def create_alternate_tree(main_node, result):
    return 0
    
	
	
def promote_alternate_tree(main_node):
    main_node.col = main_node.alt_node.col
    main_node.value = main_node.alt_node.value
    main_node.results = main_node.alt_node.results
    main_node.true_branch = main_node.alt_node.true_branch
    main_node.false_branch = main_node.alt_node.false_branch
    main_node.alt_node = None
    main_node.error = main_node.alt_node.error

# DATA VALIDATION
		
def convert_segment(segment):
    return {
        #C5
        'LIBIS_FLYOVER' : 'Libis Flyover',
        'TANDANG_SORA' : 'Tandang Sora',
        'C.P._GARCIA' : 'C.P. Garcia',
        'BONNY_SERRANO' : 'Bonny Serrano',
        'UNIVERSITY_OF_THE_PHILIPPINES' : 'University of the Philippines',
        'KALAYAAN' : 'Kalayaan',
        'ATENEO_DE_MANILA_UNIVERSITY' : 'Ateneo De Manila University',
        'LANUZA' : 'Lanuza',
        'XAVIERVILLE' : 'Xavierville',
        'MIRIAM_COLLEGE' : 'Miriam College',
		'AURORA_BOULEVARD' : 'Aurora Boulevard',
        'J._VARGAS' : 'J. Vargas',
        'CAPITOL_HILLS' : 'Capitol Hills',
        'MARKET!_MARKET!' : 'Market! Market!',
        'EASTWOOD' : 'Eastwood',
        'BAGONG_ILOG' : 'Bagong Ilog',
        'GREEN_MEADOWS' : 'Green Meadows',
        # COMMONWEALTH
        'DILIMAN_PREPARATORY SCHOOL' : 'Diliman Preparatory School',
        'UNIVERSITY_AVE' : 'University Ave',
        'GENERAL_MALVAR_HOSPITAL' : 'General Malvar Hospital',
        'EVER_GROTESCO' : 'Ever Grotesco',
        'TANDANG_SORA_EASTSIDE' : 'Tandang Sora Eastside',
        'BATASAN' : 'Batasan',
        'PHILCOA' : 'Philcoa', 
        'TANDANG_SORA_WESTSIDE' : 'Tandang Sora Westside',
        'ST._PETER\'S_CHURCH' : 'St. Peter\'s Church',
        'MAGSAYSAY_AVE' : 'Magsaysay Ave',
        'CENTRAL_AVE' : 'Central Ave',
        'ZUZUAREGI' : 'Zuzuarregi',
        # EDSA
        'NORTH_AVE.' : 'North Ave.',
        'ORENSE' : 'Orense',
        'BUENDIA' : 'Buendia',
        'TRAMO' : 'Tramo',
        'MAIN_AVE.' : 'Main Ave.',
        'TRINOMA' : 'Trinoma',
        'TIMOG_SERVICE_ROAD' : 'Timog',
        'SHAW_BLVD.' : 'Shaw Blvd.',
        'AYALA_AVE.' : 'Ayala Ave.',
        'AURORA_BLVD.' : 'Aurora Boulevard',
        'MACAPAGAL_AVE.' : 'Macapagal Ave.',
        'AURORA_BLVD._SERVICE_ROAD' : 'Aurora Blvd.',
        'MC_ARTHUR_-_FARMERS\'' : 'Mc Arthur - Farmers',
        'SHAW_BLVD._SERVICE_ROAD' : 'Shaw Blvd.',
        'TIMOG' : 'Timog',
        'AYALA_AVE._SERVICE_ROAD' : 'Ayala Ave.',
        'PIONEER_-_BONI' : 'Pioneer - Boni',
        'KAMUNING' : 'Kamuning',
        'ORTIGAS_AVE._SERVICE_ROAD' : 'Ortigas Ave.',
        'NEW_YORK_-_NEPA_Q-MART' : 'New York - Nepa Q-Mart',
        'RELIANCE' : 'Reliance',
        'SANTOLAN_SERVICE_ROAD' : 'Santolan',
        'F.B._HARRISON' : 'F.B. Harrison',
        'TAFT_AVE.' : 'Taft Ave.',
        'MAGALLANES' : 'Magallanes',
        'ARNAIZ_-_PASAY_ROAD' : 'Arnaiz - Pasay Road',
        'ORTIGAS_AVE.' : 'Ortigas Ave.',
        'PIONEER_' : 'Pioneer - Boni',
        'WHITE_PLAINS_-_CONNECTICUT' : 'White Plains - Connecticut',
        'KAINGIN_ROAD' : 'Kaingin',
        'KAMUNING_SERVICE_ROAD' : 'Kamuning',
        'ROXAS_BOULEVARD' : 'Roxas Boulevard',
        'SM_MEGAMALL' : 'SM Megamall',
        'P._TUAZON' : 'P. Tuazon',
        'GUADALUPE' : 'Guadalupe',
        'MC_ARTHUR_-_FARMERS_SERVICE_ROAD' : 'Mc Arthur - Farmers',
        'P._TUAZON_SERVICE_ROAD' : 'P. Tuazon',
        'QUEZON_AVE.' : 'Quezon Ave.',
        'KALAYAAN_-_ESTRELLA' : 'Kalayaan - Estrella',
        'BALINTAWAK' : 'Balintawak',
        'MONTE_DE_PIEDAD' : 'Monte De Piedad',
        'SANTOLAN' : 'Santolan',
        'BANSALANGIN' : 'Bansalangin',
        'MALIBAY' : 'Malibay',
        'NIA_ROAD' : 'NIA Road',
        'MU\\xc3\\xb1OZ' : 'Munoz',
        'Mu\\xc3\\x83\\xc2\\xb1oz' : 'Munoz',
		'MALL_OF_ASIA' : 'Mall of Asia',
        #ESPANA
        'WELCOME_ROTUNDA' : 'Welcome Rotunda',
        'P.NOVAL' : 'P. Noval',
        'BLUEMENTRITT' : 'Bluementritt',
        'LERMA' : 'Lerma',
        'GOV._FORBES_-_LACSON' : 'Gov. Forbes - Lacson',
        'VICENTE_CRUZ' : 'Vicente Cruz',
        'A._MACEDA' : 'A. Maceda',
        'ANTIPOLO' : 'Antipolo',
        #MARCOS HIGHWAY
        'ROBINSON\'S_METRO_EAST' : 'Robinson\'s Metro East',
        'LRT-2_STATION' : 'LRT-2 Station',
        'AMANG_RODRIGUEZ' : 'Amang Rodriguez',
        'DONA_JUANA' : 'Dona Juana',
        'F._MARIANO_AVE' : 'F. Mariano Ave',
        'SAN_BENILDO_SCHOOL' : 'San Benildo School',
        'SM_CITY_MARIKINA' : 'SM City Marikina',
        #ORTIGAS
        'EDSA_SHRINE' : 'EDSA Shrine',
        'SAN_MIGUEL_AVE' : 'San Miguel Ave',
        'GREENMEADOWS_AVE' : 'Greenmeadows Ave',
        'C5_FLYOVER' : 'C5 Flyover',
        'ROOSEVELT' : 'Roosevelt',
        'MEDICAL_CITY' : 'Medical City',
        'MERALCO_AVE' : 'Meralco Ave',
        'MADISON' : 'Madison',
        'WILSON' : 'Wilson',
        'LA_SALLE_GREENHILLS' : 'La Salle Greenhills',
        'CLUB_FILIPINO' : 'Club Filipino',
        'SANTOLAN' : 'Santolan',
        'LANUZA_AVE' : 'Lanuza Ave',
        'CONNECTICUT' : 'Connecticut',
        'POEA' : 'POEA',
        #QUEZOZ AVE
        'STO._DOMINGO' : 'Sto. Domingo',
        'MAYON' : 'Mayon',
        'SCOUT_BORROMEO' : 'Scout Borromeo',
        'SCOUT_ALBANO' : 'Scout Albano',
        'SGT._ESGUERA' : 'SGT. Esguera',
        'APO_AVENUE' : 'Apo Avenue',
        'ROCES_AVENUE' : 'Roces Avenue',
        'G._ARANETA_AVE.' : 'G. Araneta Ave.',
        'SPEAKER_PEREZ' : 'Speaker Perez',
        'SCOUT_SANTIAGO' : 'Scout Santiago',
        'SCOUT_CHUATOCO' : 'Scout Chuatoco',
        'BANTAYOG_ROAD' : 'Bantayog Road',
        'CORDILLERA' : 'Cordillera',
        'BANAWE' : 'Banawe',
        'SCOUT_MAGBANUA' : 'Scout Magbanua',
        'EDSA_SERVICE_ROAD' : 'EDSA',
        'ELLIPTICAL_ROAD' : 'Elliptical Road',
        'AGHAM_ROAD' : 'Agham Road',
        'DR._GARCIA_SR.' : 'Dr. Garcia Sr.',
        'SCOUT_REYES' : 'Scout Reyes',
        'KANLAON' : 'Kanlaon',
        'BIAK_NA_BATO' : 'Biak na Bato',
        'ROOSEVELT_AVENUE' : 'Roosevelt Avenue',
        'EDSA' : 'EDSA',
        'D._TUAZON' : 'D. Tuazon',
        #ROXAS BLVD
        'AIRPORT_ROAD' : 'Airport Road',
        'QUIRINO' : 'Quirino',
        'ANDA_CIRCLE' : 'Anda Circle',
        'EDSA_EXTENSION_CIRCLE' : 'EDSA Extension',
        'BUENDIA_SERVICE_ROAD' : 'Buendia',
        'RAJAH_SULAYMAN' : 'Rajah Sulayman',
        'BACLARAN' : 'Baclaran',
        'EDSA_EXTENSION' : 'Edsa Extension',
        'PABLO_OCAMPO' : 'Pablo Ocampo',
        'COASTAL_ROAD' : 'Coastal Road',
        'FINANCE_ROAD' : 'Finance Road',
        'U.N._AVENUE' : 'U.N. Avenue',
        'PEDRO_GIL' : 'Pedro Gil',
        #SLEX
        'BICUTAN_EXIT' : 'Bicutan Exit',
        'MERVILLE_EXIT' : 'Merville Exit',
        'ALABANG_EXIT' : 'Alabang Exit',
        'C5_ON-RAMP' : 'C5 On-ramp',
        'SUCAT_EXIT' : 'Sucat Exit',
        'NICHOLS' : 'Nichols'
    }.get(segment, segment)
		
		
def convert_street(street):
    return {
        'COMMONWEALTH' : 'Commonwealth',
        'ESPA\\xc3\\x91A' : 'Espana',
        'ROXAS_BLVD.' : 'Roxas Blvd.', 
        'ORTIGAS' : 'Ortigas',
        'QUEZON_AVE.' : 'Quezon Ave.', 
        'MARCOS_HIGHWAY' : 'Marcos Highway'
    }.get(street, street)
   
   
def street_exists(street):
    return 0

	
# convert timestamp to format : [Day of Week, Time Interval] 
def convert_timestamp(timestamp):
    timestamp = timestamp.split(' ')  # timestamp[0] = Day of Week, timestamp[1] = Day, timestamp[2] = Month, timestamp[3] = Year, timestamp[4] = Time
    dayOfWeek = timestamp[0].replace(',', '')
    time = timestamp[4]
    time_interval = convert_time_interval(time)
	
    time_fields = list()
    time_fields.append(dayOfWeek)
    # time_fields.append(month)
    time_fields.append(time_interval)

    return time_fields
		
		
# converts time in HH:MM format to time interval
def convert_time_interval(time):
    print("Converting HH:MM time to time interval")
    split_stamp = str(time).split(':')
    split_stamp1 = split_stamp[0]
    split_stamp2 = split_stamp[1]
    interval = int(round((((int(split_stamp1) * 60)) + (int(split_stamp2))) / 15))
    print(interval)
    return interval


def convert_time_standard(time):
    print("ENTERED convert_time_standard")
    print("Time received: " + time)
    temp = time.split(' ')
    hold_AMPM = temp[1]
    print("AM/PM: " + hold_AMPM)
    trim_time = temp[0]
    print("Trimmed time: " + trim_time)
    split_time = trim_time.split(':')
    if temp[1] == 'PM':
        if(int(split_time[0]) < 12):
            split_time[0] = str(int(split_time[0]) + 12)
    print(split_time[0] + ':' + split_time[1])
    return split_time[0] + ':' + split_time[1]
	
	
def get_day_of_week(date):
    date_object = datetime.strptime(date, '%m-%d-%Y')
    day_int = date_object.weekday()
    if day_int == 0:
        return 'Mon'
    elif day_int == 1:
        return 'Tue'
    elif day_int == 2:
        return 'Wed'
    elif day_int == 3:
        return 'Thu'
    elif day_int == 4:
        return 'Fri'
    else:
        return 'Sun'
	
def read_row(row):
    new_row = list(row) # 0 - location_road (street), 1 - location_bound, 2 - location_area(segment), 3 - timestamp, 4 - traffic
    new_row[0] = convert_street(new_row[0].strip())
    new_row[2] = convert_segment(new_row[2].strip())
    timestamp = new_row[3]
    traffic = new_row[4]
	
    del new_row[4] # delete traffic
    del new_row[3] # delete timestamp 
    del new_row[1] # delete location_bound

    new_time = convert_timestamp(timestamp)
    for time_field in new_time:
        new_row.append(time_field)
    new_row.append(traffic)
	
    return new_row
		
		
# SYSTEM ARGUMENTS
def initialize_tree():

    time_start = time.clock()

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
        cur.execute("""SELECT location_road, location_bound, location_area, timestamp, traffic FROM entries WHERE (update_timestamp > timestamp '2017-03-07 00:00:00' AND update_timestamp < timestamp '2017-03-08 00:00:00') OR (update_timestamp > timestamp '2017-03-14 00:00:00' AND update_timestamp < timestamp '2017-03-15 00:00:00') OR (update_timestamp > timestamp '2017-03-21 00:00:00' AND update_timestamp < timestamp '2017-03-22 00:00:00')""")
    except:
        print("Data retrieval failed.")

    data = cur.fetchall()
    data_list = list()

    for row in data:  # Street, Segment, Day of Week, Time Interval, Traffic Condition
        new_row = read_row(row)
        data_list.append(new_row)

        # Result: row[0] = Street, row[1] = Segment, row[2] = Day of Week, row[3] = Time Interval, row[5] = Traffic

        print("After conversion: ")
        print(new_row)
        print("\n")

    data = list(data_list)
    print("Data retrieved.")

    print("Building tree...\n")
    result = buildtree(data)
    print("Tree built.")

    # printtree(result)

    time_end = time.clock()
    instance_count = data.__len__()
    process_time = time_end - time_start

    print("Instances: ")
    print(instance_count)
    print("Processing Time: ")
    print(process_time)

    # SAVE TREE
    print("Saving model...")
    try:
        pickle.dump(result, open("model.p", "wb"))
        print("Model saved.")
    except:
        print("Saving failed.")


def get_prediction(street, segment, date, time):
    # load tree data
    data = pickle.load(open("model.p", "rb"))
	
    day_of_week = get_day_of_week(date)
    time_interval = convert_time_interval(convert_time_standard(time))
	
    print("Street: " + street)
    print("Segment: " + segment)
    print("Day of week: " + day_of_week)
    print("Time Interval: " + str(time_interval))
    return classify([street, segment, day_of_week, time_interval], data)

	
def set_last_update():
	return 0

	
def update_tree(date, time):
    return 0


def print_traffic_model():
    data = pickle.load(open("model.p", "rb"))
    printtree(data)


# MAIN

# Web Code

# System Argument Code

arguments = sys.argv

print(arguments)

if str(arguments[1]) == 'init': # initializes tree (WARNING: OVERWRITES MODEL FILE)
    initialize_tree()
elif str(arguments[1]) == 'predict': # Gets a prediction based on given parameters (Parameters: street, date (MM-DD-YYYY), time (00:00 AM/PM))
    print(get_prediction("EDSA", "Shaw", "07-05-2017", "12:30 PM"))
elif str(arguments[1]) == 'update': # Updates tree with instances from date/time of last instance parsed until given date/time (Parameters: date(MM-DD-YYYY, time (HH:MM))
    update_tree(str(arguments[1]), str(arguments[2]))
elif str(arguments[1]) == 'print_tree': # prints traffic model
    print_traffic_model()
	
'''
elif str(arguments[1]) == 'run_server':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), request_handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
'''
'''
HOST_NAME = ''
PORT_NUMBER = 8080

class request_handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
 
    def do_GET(s):
        from urlparse import urlparse
        query = urlparse(s.path).geturl()
		
		# Process Query
        query = query[1:]
        query = query.replace("%20", " ")
        query_components = query.split("&")
		
        if len(query_components == 4):
		
            street = query_components[0]
            segment = query_components[1]
            date = query_components[2]
            time = query_components[3]
            # from street, segment, date, time
            prediction = get_prediction(street, segment, date, time) # passes street, segment, day of week, month, time interval
		
            # Create Response
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write("<html><head><title>Prediction Result</title></head>")
            s.wfile.write("<body><p>" + prediction + "</p></body></html>")

        else:
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write("<html><head><title>Prediction Result</title></head>")
            s.wfile.write("<body><p>Invalid Arguments</p></body></html>")
'''

# print("Predicting traffic for ORTIGAS-SB-C5_FLYOVER on a Wednesday at time interval 47")
#print(classify(['ORTIGAS-SB-C5_FLYOVER', 'Wed', 47], result))
