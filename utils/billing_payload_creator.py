import json
import MySQLdb
import gzip
import argparse
import getpass
from datetime import datetime, timedelta
import requests

# Default values for command line args
cdb_host_default = '127.0.0.1'
cdb_mariadb_user_default = 'root'
cdb_mariadb_password_default = 'em7admin'

# get your username/password from ScienceLogic
billingserver_user_default = ''
billingserver_password_default = ''

# format: http://username:password@proxy-hostname-or-ip:port, for example: http://user101:mypassword@proxy.company-a.com:8080
proxy_url_default = ''

# this is a fixed value
billingserver_root_url = 'https://billing.sciencelogic.com'

def debug(level, details):
    print("{}: {}".format(level, details))

def get_args():
    parser = argparse.ArgumentParser(description='Dump license data into a gzipped JSON file, for transmitting back to ScienceLogic billing service.')
    parser.add_argument('--host', help='Optional --  CDB hostname', required=False, default=cdb_host_default)
    parser.add_argument('--db_user', help='Optional --  CDB MariaDB username', required=False, default=cdb_mariadb_user_default)
    parser.add_argument('--db_password', help='Optional --  CDB MariaDB password', required=False, default=cdb_mariadb_password_default)
    parser.add_argument('--billing_user', help='Optional --  Billing server username', required=False, default=billingserver_user_default)
    parser.add_argument('--billing_password', help='Optional --  Billing server password', required=False, default=billingserver_password_default)
    parser.add_argument('--output_dir', help='Optional --  directory for output files, default = /tmp', required=False, default='/tmp')
    parser.add_argument('--proxy', help='Optional -- Proxy settings', required=False, default=proxy_url_default)

    # dump yesterday's usage by default
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') + ' 00:00:00'

    parser.add_argument('--date', help='Optional --  date string of daily usage, e.g. "2020-01-30 00:00:00"', required=False, default=yesterday)
    args = vars(parser.parse_args())
    return args

def query_usage(args):
    DB_HOST = args['host']
    DB_USER = args['db_user']
    DATE = args['date']
    DB_PASS = args['db_password']
    try:
        db = MySQLdb.connect(host=DB_HOST,
                             user=DB_USER,
                             passwd=DB_PASS,
                             db="subscriber_data",
                             port=7706,
                             connect_timeout=10)
        cur = db.cursor()
        cur.execute("SELECT CAST(storage_time AS CHAR) AS storage_time, dev_config, dev_stats, sys_config, sys_stats FROM `subscriber_data`.`data_daily` WHERE storage_time = '%s';" % DATE)
        row = cur.fetchone()
        data = {"storage_time": row[0], "dev_config": row[1], "dev_stats": row[2], "sys_config": row[3], "sys_stats": row[4]}
        return True, data
    except Exception as ex:
        return False, ex

def billingserver_login(args):
    user = args['billing_user']
    password = args['billing_password']
    proxies = {"http": args['proxy']}
    url = billingserver_root_url + '/login.em7'
    resp = session.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        proxies=proxies,
        data = {
            'LOGIN_user[]': user,
            'LOGIN_pwd[]': password,
            'signon': 1,
        }
    )
    return resp

def upload_usage(args, filename):
    user = args['billing_user']
    password = args['billing_password']
    proxies = {"http": args['proxy']}
    # url = billingserver_root_url + '/report_usage.em7'
    url = billingserver_root_url + '/em7/index.em7?exec=my&act=my_subscription'
    with open(filename, 'rb') as f:
        resp = session.post(
            url,
            headers = {
                "Content-Type": "appliction/gzip"
                # "Content-Type": "multipart/form-data"
            },
            proxies=proxies,
            files = {'file': f}
        )
    return resp

### MAIN ###
args = get_args()
success, data = query_usage(args)
if success == False:
    debug("ERROR", "Error retrieving usage data, exit.")
    exit(2)
j = json.dumps(data)
output_dir = args['output_dir']
output_file = output_dir + '/' + args['date'].replace(' ', '_') + '.json.gz'
debug("INFO", "Output file - " + output_file)

with gzip.open(output_file, 'wb') as f:
    f.write(j)

session = requests.Session()

resp = billingserver_login(args)
if resp.status_code == 200:
    debug("INFO", "Logged in to billing server successfully.")
else:
    debug("ERROR", "Could not login to billing server.")
    exit(1)

resp = upload_usage(args, output_file)
if resp.status_code == 200:
    print(resp.text)
