#!/opt/em7/bin/python

import argparse
import getpass
import MySQLdb
from datetime import datetime

def populate_table(table_name, no_of_trx, value_of_trx):
    stm = "insert into {} (app_id, no_of_trx, value_of_trx) values (0, {}, {}) on duplicate key update no_of_trx = {}, value_of_trx = {}".format(table_name, no_of_trx, value_of_trx, no_of_trx, value_of_trx)
    debug(stm)
    cursor.execute(stm)
    db.commit()

def debug(msg):
    if log is True:
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print("{}: {}".format(dt_string, msg))

####################### MAIN #######################
log = True
parser = argparse.ArgumentParser(description='Populating database perf data for silo demo.')
parser.add_argument('--table', help='Required argument --  table to be populated in database "business_services"', required=True)
parser.add_argument('--source', help='Required argument --  source file to read the perf data.', required=True)
args = vars(parser.parse_args())

table_name = args['table']
source_file = args['source']

db = MySQLdb.connect(
    host = '127.0.0.1',
    user = 'root',
    passwd = 'em7admin',
    db = 'business_services',
    port = 7707)
cursor = db.cursor()
cursor.execute("select * from counter")
i = cursor.fetchone()[0]

# find the line indexed by i
try:
    with open(source_file) as fp:
        found = False
        line0 = "" # just in case we need line 0
        for j, line in enumerate(fp):
            if j == 0:
                line0 = line
            if i == j:
                debug("Current source line: {}".format(line))
                found = True
                i = i + 1
                stm = "update counter set i = {};".format(i)
                debug(stm)
                cursor.execute(stm)
                db.commit()

                # populate table with the current line
                v = line.split()
                populate_table(table_name, v[0], v[1])
                break
        if not found:
            debug("Reset the counter..")
            stm = "update counter set i = 1;"
            debug(stm)
            cursor.execute(stm)
            db.commit()

            debug("line0: {}".format(line0))
            v = line0.split()
            populate_table(table_name, v[0], v[1])
            exit(1)
except IOError:
    debug("Source file not accessible")
    db.close()
    exit(2)

db.close()
