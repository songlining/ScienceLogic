import cPickle as pickle

logger=em7_snippets.logger(filename='/tmp/em7_vars.log')

g = globals()
em7_vars = {}
for k in list(g):
    if 'EM7' in k:
        em7_vars[k] = g[k]
p = pickle.dumps(em7_vars)
logger.debug ("EM7 variable dump starts here: ")
logger.debug (">>>" + p + "<<<")
logger.debug ("EM7 variable dump stops here.")

