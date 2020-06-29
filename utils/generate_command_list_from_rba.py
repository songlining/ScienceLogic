from silo_common.database import local_db
import re
import json
dbc = local_db()

html_content = ''

debug = 0

content = {}
# Sample and data structure below
# content = {
#     "Cisco: CSP Cluster Creation": { # automation policy name, supposed to be an unique key
#         "event_names": ["Cisco: CSP Cluster Creation"], # one or more events aligned to this automation
#         "actions": {
#             "Cisco: CSP Cluster Creation": []
#             "Cisco: CSP Cluster Creation Write Back": []
#         }
#     }
# }

def extract_from_snippet_headers():

    query = '''
    SELECT a.policy_name, e.ename, actions.action_name, s.snippet_code
    FROM master.policies_events as e
    INNER JOIN master.policies_automation_events as ae on e.id = ae.eid
    INNER JOIN master.policies_automation as a on a.ap_id = ae.ap_id
    INNER JOIN master.policies_automation_lookup as al on al.ap_id = a.ap_id
    INNER JOIN master.policies_actions as actions on actions.action_id = al.action_id
    INNER JOIN master.policies_actions_snippet as s on s.action_id = actions.action_id
    '''
    actions = dbc.autofetchall_dict(query)
    for d in actions :
        ap_name = d["policy_name"].strip()
        ename = d["ename"].strip()
        action_name = d["action_name"].strip()
        snippet_code = d["snippet_code"]
        parsed_snippet = re.search('("""[^@]+""")', snippet_code, re.DOTALL) # testing for entries without "@"
        parsed_snippet_cli = re.search('"""(.*?@command.*?)"""', d['snippet_code'], re.DOTALL)
        if parsed_snippet_cli is not None:
            snippet_head = parsed_snippet_cli.group(1)
            lines = snippet_head.split("\n")
            commands = []
            for line in lines:
                if line.startswith("@command"):
                    commands.append(line.strip().strip("@command: ").strip("\r").strip('"'))
            populate_json(ap_name, ename, action_name, commands)
        else:
            populate_json(ap_name, ename, action_name, [])


def extract_from_action_types():

    query = '''
    SELECT a.policy_name, e.ename, actions.action_name, t.in_param_val
    FROM master.policies_events as e
    INNER JOIN master.policies_automation_events as ae on e.id = ae.eid
    INNER JOIN master.policies_automation as a on a.ap_id = ae.ap_id
    INNER JOIN master.policies_automation_lookup as al on al.ap_id = a.ap_id
    INNER JOIN master.policies_actions as actions on actions.action_id = al.action_id
    INNER JOIN master.policies_actions_types as t on t.action_id = actions.action_id
    '''
    actions = dbc.autofetchall_dict(query)
    for d in actions :
        ap_name = d["policy_name"].strip()
        ename = d["ename"].strip()
        action_name = d["action_name"].strip()
        json_content = d["in_param_val"]

        commands = []
        j = json.loads(json_content)
        if "commands" in j:
            c1 = j['commands']
            try:
                j = json.loads(c1)
                if "commands" in j:
                    c2 = j['commands']
                    commands = c2
            except Exception:
                # We got the command name here
                commands.append(c1)
        populate_json(ap_name, ename, action_name, commands)

def populate_json(ap_name, ename, action_name, commands):

    global content

    if ap_name not in content:
        content[ap_name] = {}
        content[ap_name]["event_names"] = []
        content[ap_name]["actions"] = {}
    if ename not in content[ap_name]["event_names"]:
        content[ap_name]["event_names"].append(ename)
    if action_name not in content:
        content[ap_name]["actions"][action_name] = commands

def print_html():

    global content
    counter = 1
    html_content = ''
    rows = ''

    for ap_name in content:
        rowspan = len(content[ap_name]["actions"])
        if rowspan == 0:
            rowspan = 1
        events = ''
        for e in content[ap_name]["event_names"]:
            events = events + '<br>' + e
        rows = rows + '<tr><td rowspan="{}">{}</td><td rowspan="{}">{}</td><td rowspan="{}">{}</td>'.format(rowspan, counter, rowspan, ap_name, rowspan, events)
        first_row = True
        if rowspan == 0:
            # no actions in this automation has any meaningful commands
            rows = rows + '<td></td><td></td></tr>'
        else:
            for action_name in content[ap_name]['actions']:
                commands = ''
                for c in content[ap_name]['actions'][action_name]:
                    commands = commands + '<br>' + c
                if first_row:
                    # first row will be a full span of all cells
                    rows = rows + '<td>{}</td><td>{}</td></tr>'.format(action_name, commands)
                    first_row = False
                else:
                    rows = rows + '<tr><td>{}</td><td>{}</td></tr>'.format(action_name, commands)

        rows = rows + '\n'
        counter = counter + 1

    html_content = """<html>\n<table border="1" class="dataframe">
    <thead>
      <tr style="text-align: left;">
        <th>#</th>
        <th>Automation Policy</th>
        <th>Event Policy</th>
        <th>Action Policy</th>
        <th>Command</th>
    </tr>
    </thead>
    <tbody>""" + rows + "</tbody>\n</table>\n</html>"

    print html_content

extract_from_action_types()
extract_from_snippet_headers()
print_html()

#print(json.dumps(content))
