# The code block below is for manual triggering of the Action. It will be bypassed if it's triggered by an Automation.
if 'EM7_VALUES' not in globals():
    import cPickle as pickle
    with open("./em7_vars.pk", 'r') as f:
        d = pickle.loads(f.read())

    for k in d:
        if 'EM7' in k:
            vars()[k] = d[k]

    d = None
