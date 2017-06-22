import psycopg2
import time
import sys
import pickle


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
    def __init__(self, col=-1, value=None, results=None, true_branch=None, false_branch=None, alt_node=None, error=0):
        self.col = col
        self.value = value
        self.results = results
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.alt_node = alt_node
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


def printtree(tree, indent=''):
    if tree.results != None:
        print("Prediction: ", str(tree.results), "; error_rate: ", str(tree.error))
    else:
        if tree.col == 0:
            col_name = "STREET"
        elif tree.col == 1:
            col_name = "DAY OF WEEK"
        elif tree.col == 2:
            col_name = "TIME INTERVAL"
        else:
            col_name = str(tree.col)
        print(col_name + ':'+str(tree.value)+'? ')
        # Print the branches
        print(indent+'T->', end=" ")
        printtree(tree.true_branch, indent + '  ')
        print(indent+'F->', end=" ")
        printtree(tree.false_branch, indent + '  ')


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


# TREE LOADING/SAVING

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
        cur.execute("""SELECT location_road, location_bound, location_area, timestamp, traffic FROM entries WHERE location_road = 'EDSA' AND location_bound = 'NB' AND location_area = 'MALL_OF_ASIA'""")
    except:
        print("Data retrieval failed.")

    data = cur.fetchall()
    data_list = list()

    for row in data:  # Street, Day of Week, Time Interval, Traffic Condition

        new_row = list(row)
        print("Raw row: ")
        print(new_row)

        # combines location elements
        new_row[0] = '-'.join(new_row[0:3]) # 0 - Street, 1 - timestamp, 2 - traffic

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
        interval = int(round(((int(split_stamp[0]) * 60) + int(split_stamp[1])) / 15))

        traffic_con = new_row[2]

        # adds new time elements into row
        del new_row[1]
        del new_row[1]

        new_row.append(day_of_week)
        new_row.append(interval)
        new_row.append(traffic_con)

        data_list.append(new_row)

        # Result: row[0] = Street, row[1] = Day of Week, row[2] = Time Interval

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


def get_prediction(street, date, time):
    # load tree data
    data = pickle.load(open("model.p", "rb"))
    print(classify(street, day, time))


def update_tree(street, date, condition):
    return 0


def print_traffic_model():
    data = pickle.load(open("model.p", "rb"))
    printtree(data)


# MAIN

arguments = sys.argv

print(arguments)

if str(arguments[1]) == 'init':
    initialize_tree()
elif str(arguments[1]) == 'predict':
    print(get_prediction(str(arguments[2]), str(arguments[3]), arguments[4])))
elif str(arguments[1]) == 'update':
    update_tree(str(arguments[1]), str(arguments[2]), str(arguments[3]))
elif str(arguments[1]) == 'print_tree':
    print_traffic_model()




# print("Predicting traffic for ORTIGAS-SB-C5_FLYOVER on a Wednesday at time interval 47")
#print(classify(['ORTIGAS-SB-C5_FLYOVER', 'Wed', 47], result))
