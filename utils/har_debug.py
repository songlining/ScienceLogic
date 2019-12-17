#!/usr/bin/env python

import requests
import re
import argparse
import getpass
import urllib3

urllib3.disable_warnings()

def run_gql(url, payload, auth): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post(url, json=payload, verify=False, auth=auth)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("GraphQL query failed to run by returning code of {}. \n\nOriginal Query: {}".format(request.status_code, query))

####### main ######

parser = argparse.ArgumentParser(description='This script helps to pinpoint failed BS rules.')
parser.add_argument('--url', help='Required argument --  URL of the SL1 GraphQL API endpoint.  Example: https://sl1platform.company.com/gql OR http://sl1platform.company.com/gql', required=True)
parser.add_argument('--user', help='Required argument --  user name for the GraphQL request.  Users will be prompted for a password at run time.', required=True)
args = vars(parser.parse_args())

GQL_URL = args['url']
username = args['user']
password = getpass.getpass(prompt='Password: ')

query = """
query onDemand {
  harProviderOnDemandProcessing(ids: []) {
    results { serviceId timestamp health availability risk }
    auditHistory { serviceId ruleSetId ruleId timestamp sequence message }
  }
}
"""

variables = """
{
}
"""

payload = {
    'query': query,
    'variables': variables
}

auth = (username, password)
try:
    result = run_gql(GQL_URL, payload, auth) # Execute the query
except Exception as e:
    print ("Error caught: {}".format(e))
    exit(1)
for r in result['data']['harProviderOnDemandProcessing']['auditHistory']:
    if r['message'].count('null'):
        parsed_message = re.search('Service:\s(.*?)\sPolicy:\s(.*?)\sRule.*Set: (.*?):',r['message'])
        if parsed_message is not None:
            print ("Business Service :{}".format(parsed_message.group(1)))
            print ("Policy           :{}".format(parsed_message.group(2)))
            print ("Rule Type        :{}".format(parsed_message.group(3)))
            if parsed_message.group(3).count('Rule') >0:
                print ("Complete message :{}".format(r['message']))
            print ("\n")
