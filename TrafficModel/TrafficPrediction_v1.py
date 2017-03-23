import psycopg2

# DB Connect

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

for row in data: # Street, Day of Week, Time Interval, Traffic Condition
    # combines location elements
    row[0:2] = ['-'.join(row[0:2])] 
    
    # splits timestamp into day and time interval
    timestamp = row[1].split(' ') # timestamp[0] = Day of Week, timestamp[1] = Day, timestamp[2] = Month, timestamp[3] = Year, timestamp[4] = Time

    # delete not needed time information (timestamp[0] = Day of Week, timestamp[1] = Time)
    timestamp.del(timestamp[3]) # deletes year
    timestamp.del(timestamp[2]) # deletes month
    timestamp.del(timestamp[1]) # deletes day
    timestamp[0] = timestamp[0].replace(',', '')
    
    # convert time to interval value
    time = timestamp[1].split(':')
    timestamp[1] = ((int(time[0]) * 60) + int(time[1])) / 15

    # adds new time elements into row
    row.del(1)
    row.extend(timestamp)

    # Result: row[0] = Street, row[1] = Day of Week, row[2] = Time Interval
        


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
        if r not in results: results[r] = 0
        results[r] += 1
    return results


def entropy(rows):
    from math import log
    log2 = lambda x:log(x)/log(2)
    results = countunique(rows)
    ent = 0.0
    for r in results.keys():
        p = float(results[r])/len(rows)
        ent = ent-p*log2(p)
    return ent


class TreeNode:
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb


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
                            tb=true_branch, fb=false_branch)
    else:
        return TreeNode(results=countunique(rows))


def printtree(tree, indent=''):
    if tree.results != None:
        print(str(tree.results))
    else:
        print(str(tree.col)+':'+str(tree.value)+'? ')
        # Print the branches
        print(indent+'T->', end=" ")
        printtree(tree.tb,indent+'  ')
        print(indent+'F->', end=" ")
        printtree(tree.fb,indent+'  ')


def classify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        obs = observation[tree.col]
        branch = None
        if isinstance(obs, int) or isinstance(obs, float):
            if obs >= tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        else:
            if obs == tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        return classify(observation, branch)

result = buildtree(data)
printtree(result)
print(classify(['street2', 'Monday', 5], result))

