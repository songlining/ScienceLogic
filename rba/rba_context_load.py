# The code block below is for manual triggering of the Action. It will be bypassed if it's triggered by an Automation.
if 'EM7_VALUES' not in globals():
    import json
    with open("./em7_vars.json", 'r') as f:
        j = json.load(f)
    for k in j:
        if 'EM7' in k:
            vars()[k] = j[k]

    j = None
