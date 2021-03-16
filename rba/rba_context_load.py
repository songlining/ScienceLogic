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
