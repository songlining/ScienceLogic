#!/usr/bin/env python

import requests
import re
import argparse
import getpass
import urllib3
from tabulate import tabulate
from string import Template
urllib3.disable_warnings()

def run_gql(url, payload, auth): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post(url, json=payload, verify=False, auth=auth)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("GraphQL query failed to run by returning code of {}. \n\nOriginal Query: {}".format(request.status_code, query))

def list_bs():
    query = """
query HarProviderSearch($search: HarProviderSearch, $cursor: String, $sort: [ConnectionOrder]) {
  harProviders(first: 5000000, search: $search, after: $cursor, order: $sort) {
    pageInfo {
      hasPreviousPage
      hasNextPage
      matchCount
      __typename
    }
    edges {
      cursor
      node {
        ...hp
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment hp on HarProvider {
  id
  name
  type
  applicationsInBusinessService
  description
  rootCauseAnalysisMode
  policy {
    id
    name
    isDefault
    validationErrors
    __typename
  }
  health
  availability
  risk
  filter {
    id
    filter
    search
    hash
    version
    searchJson
    __typename
  }
  referenceFilter {
    id
    filter
    search
    hash
    version
    searchJson
    __typename
  }
  hasIcon
  icon {
    id
    __typename
  }
  contactUser {
    id
    contact {
      firstName
      __typename
    }
    __typename
  }
  contactOrganization {
    id
    company
    __typename
  }
  organization {
    id
    company
    __typename
  }
  additionalOrganizations {
    id
    company
    __typename
  }
  searchInAdditionalOrganizations
  __typename
}
"""

    variables = """
{
    "search": {
        "and": [
            {},
            {
                "type": {
                    "in": [
                        "businessService",
                        "itService",
                        "deviceService"
                    ]
                }
            }
        ]
    },
    "sort": []
}
"""

    payload = {
        'query': query,
        'variables': variables
    }
    auth = (username, password)
    try:
        result = run_gql(GQL_URL, payload, auth) # Execute the query
        return result
    except Exception as e:
        print ("Error caught: {}".format(e))
        exit(1)

def delete_bs(id):
    query = """
      mutation deleteHarProvider($id: ID!) {
        deleteHarProvider(id: $id)
      }
    """

    variables = """
    {
        "id": "$id"
    }
    """

    v = Template(variables).safe_substitute(id = id)
    payload = {
        'query': query,
        'variables': v
    }
    auth = (username, password)
    try:
        result = run_gql(GQL_URL, payload, auth) # Execute the query
        return result
    except Exception as e:
        print ("Error caught: {}".format(e))
        exit(1)

####### main ######

parser = argparse.ArgumentParser(description='Batch deletion of Business Services.')
parser.add_argument('--url', help='Required argument --  URL of the SL1 GraphQL API endpoint.  Example: https://sl1platform.company.com/gql OR http://sl1platform.company.com/gql', required=True)
parser.add_argument('--user', help='Required argument --  user name for the GraphQL request.  Users will be prompted for a password at run time.', required=True)
parser.add_argument('--org', help='Required argument --  SL1 Organization.')
args = vars(parser.parse_args())

GQL_URL = args['url']
username = args['user']
organization = args['org']
print("org = {}".format(organization))
password = getpass.getpass(prompt='Password: ')

try: input = raw_input
except NameError: pass

while True:
    result = list_bs()
    table = []
    n = 0
    for e in result['data']['harProviders']['edges']:
        node = e['node']
        name = node['name']
        id = node['id']
        type = node['type']
        org = node['organization']['company']
        if organization is not None and org != organization:
            continue
        table.append([n, name, type, org, id])
        n = n + 1
    print(tabulate(table, headers=["Index", "Name", "Type", "Organization", "ID"]))
    i = input("\nEnter the index numbers from the above table, separated by space, press Enter once finished: ")
    bs_index = i.split()
    for i in bs_index:
        try:
            bs_id = table[int(i)][4]
            result = delete_bs(bs_id)
            print(result)
        except Exception as e:
            print ("Index: {}, Error caught: {}".format(i, e))
            continue
