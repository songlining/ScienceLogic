import json

logger=em7_snippets.logger(filename='/tmp/em7_vars.log')

g = globals()
em7_vars = {}
for k in list(g):
    if 'EM7' in k:
        em7_vars[k] = g[k]
try: 
    j = json.dumps(em7_vars, indent = 4).encode('utf8')
    logger.debug ("EM7 variable dump starts here: ")
    logger.debug (">>>" + j + "<<<")
    logger.debug ("EM7 variable dump stops here.")
except Exception as ex:
    logger.debug ("json dump error: {}. This can be ignored in most cases".format(ex))

