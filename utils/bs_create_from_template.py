#!/usr/bin/env python

import requests
import re
import argparse
import getpass
import urllib3
import inquirer
import json
from string import Template
from pprint import pprint
urllib3.disable_warnings()

def run_gql(url, payload, auth): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post(url, json=payload, verify=False, auth=auth)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("GraphQL query failed to run by returning code of {}. \n\nOriginal Query: {}".format(request.status_code, query))

def list_templates():
    query = """
fragment harTemplate on HarTemplate {
  id
  harProviderType
  name
  description
  definition
  __typename
}

query harTemplates($search: HarTemplateSearch, $order: [ConnectionOrder], $cursor: String) {
  harTemplates(search: $search, order: $order, first: 30, after: $cursor) {
    edges {
      node {
        ...harTemplate
        __typename
      }
      cursor
      __typename
    }
    pageInfo {
      hasNextPage
      matchCount
      __typename
    }
    __typename
  }
}
"""

    variables = """
{
    "search": {
        "and": [
            {},
            {
                "harProviderType": {
                    "in": [
                        "businessService",
                        "itService",
                        "deviceService"
                    ]
                }
            }
        ]
    },
    "order": [
        {
            "field": "name",
            "direction": "asc"
        }
    ]
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

def fetchOne(template_id):
    query = '''
    query fetchOne ($templateId: ID!) {
    harTemplate (id: $templateId){
      id
      name
      harProviderType
      description
      definition
    }
  }
    '''
    variables = '''
    {
    "templateId": "$id"
    }
    '''

    v = Template(variables).safe_substitute(id = template_id)

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

def createFromHarTemplate(template_id, bs_name, bs_description, definition):

    query = '''
    mutation createFromHarTemplate($templateId: ID!, $name: String!, $definition: JSON!) {
      createFromHarTemplate(id: $templateId, name: $name, definition: $definition) {
        harProviders { id  name } harPolicies { id name }
      }
    }
    '''

    variables = '''
    {
      "templateId": "$template_id",
      "name": "$bs_name",
      "definition": $definition
    }
    '''

    definition['harProviders'][0]['name'] = bs_name
    definition['harProviders'][0]['description'] = bs_description

    definition_json = json.dumps(definition)

    v = Template(variables).safe_substitute(template_id = template_id, bs_name = bs_name, definition = definition_json)

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

parser = argparse.ArgumentParser(description='Create Business Services from Templates.')
parser.add_argument('--url', help='Required argument --  URL of the SL1 GraphQL API endpoint.  Example: https://sl1platform.company.com/gql OR http://sl1platform.company.com/gql', required=True)
parser.add_argument('--user', help='Required argument --  user name for the GraphQL request.  Users will be prompted for a password at run time.', required=True)
args = vars(parser.parse_args())

GQL_URL = args['url']
username = args['user']
password = getpass.getpass(prompt='Password: ')

result = list_templates()
choices_templates = []
for e in result['data']['harTemplates']['edges']:
    node = e['node']
    name = node['name']
    id = node['id']
    choices_templates.append((name, id))

questions = [
    inquirer.List(
        "id",
        message = "Choose a template: ",
        choices = choices_templates
    ),
]

answers = inquirer.prompt(questions)
template_id = answers["id"]
bs_name = input("\nName of the Business Service: ")
bs_description = input("\nDescription of the Business Service: ")

r = fetchOne(template_id)
definition = r['data']['harTemplate']['definition']
createFromHarTemplate(template_id, bs_name, bs_description, definition)
