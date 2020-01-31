#!/usr/bin/env python3

import requests
import re
import sys
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

request = requests.session()


if( len(sys.argv) != 2):
	print ("(-) usage curl1.py target")
	exit()

target = sys.argv[1]

r = requests.get('http://' + target, allow_redirects=True, verify=False)
#print (r.headers)
rh = json.dumps(r.headers.__dict__['_store'])


searchObj = re.search('citrix_ns_id', rh)

if searchObj:
	print (searchObj.group())
	print ("There is a Citrix WAF")
else:
	print ("(-)This is not a Citrix")