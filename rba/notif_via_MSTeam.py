import requests

#############################################################################
# This code block is for manual triggering of the Action. It will be bypassed
# if it's triggered by an Automation, therefore it can be kept in production
# code.
#############################################################################
if 'EM7_VALUES' not in globals():
    import cPickle as pickle
    with open("./em7_vars.pk", 'r') as f:
        d = pickle.loads(f.read())
    for k in d:
        if 'EM7' in k:
            vars()[k] = d[k]
    d = None

    ###################################################
    # input variables from action types (if any) below
    ###################################################

    # webhook and classic_ui are variables defined in the Action Type
    # change the value below to your own webhook
    webhook = "https://company-a.webhook.office.com/webhookb2/..."
    # construct the event uri either by its classic format or ap2 format
    classic_ui = False

message = EM7_VALUES['%M']
system  = EM7_VALUES['%X']
sev     = EM7_VALUES['%S']
dt      = EM7_VALUES['%d']
ip      = EM7_VALUES['%a']
uri     = EM7_VALUES['%H']
event   = EM7_VALUES['%e']

def extract_action_logs():
    action_logs = ''
    for r in EM7_LAST_RESULT_LIST:
        # we only extract values in string type
        if isinstance(r.result, str):
            action_logs = action_logs +'<br><hr>' + r.result
    if action_logs == '':
        return 'n/a'
    else:
        return action_logs

action_logs = extract_action_logs()

if classic_ui == False:
    # converting from: https://sl1.company-a.com/em7/index.em7?exec=events&q_type=aid&q_arg=789088&q_sev=1&q_sort=0&q_oper=0 
    #              to: https://sl1.company-a.com/events/detail/789088
    uri     = uri.split("/em7/index.em7")[0]+'/events/detail/' + event

task = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "7B83EB",
    "summary": "ScienceLogic Event Notification",
    "sections": [{
        "activityTitle": system,
        "activitySubtitle": ip,
        "facts": [{
            "name": "Severity",
            "value": sev
        }, {
            "name": "Event Message",
            "value": message
        }, {
            "name": "Event Date",
            "value": dt
        }, {
            "name": "Event ID",
            "value": event
        },{
            "name": "Action Logs",
            "value": action_logs
        }]
    }],
    "potentialAction": [  {
        "@type": "OpenUri",
        "name": "Event Link",
        "targets": [{
            "os": "default",
            "uri": uri
        }]
    }]
}

resp = requests.post(webhook, json=task)

EM7_RESULT = str(resp.status_code)+":"+resp.reason+":"+resp.url
