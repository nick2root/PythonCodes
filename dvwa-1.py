#!/usr/bin/env python3

import requests
import re
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


if( len(sys.argv) < 4):
	print ("(-) usage dvwa-1.py target username password")
	exit()

target = sys.argv[1]

username = sys.argv[2]

password = sys.argv[3]
security_level = "low"

url = 'http://' + target + '/DVWA/login.php'

def csrf_token():
    try:
        #make request to the URL
        print ("\n[i] URL: %s/DVWA/login.php" %target)
        r = requests.get(url, allow_redirects= False)
    except:
        #feedback for the user
        print ("\n[!] csrf_token: Failed to connect URL. \n[i] Quiting")
        sys.exit(-1)

    #Extract anti-csrf token
    source = BeautifulSoup(r.text, "html.parser")
    user_token = source("input", {"name": "user_token"})[0]["value"]
    print (user_token)
    print ("[i] user_token: %s" % user_token)

    #Extract session information
    session_id = re.match("PHPSESSID=(.*?);", r.headers["set-cookie"])
    session_id = session_id.group(1)
    print ("[i] session_id: %s" % session_id)

    return session_id, user_token

#Login to DVWA
def dvwa_login(session_id, user_token):
    #POST DATA
    data = { "username": username, "password": password, "user_token": user_token, "Login": "Login"}
    cookie = {"PHPSESSID": session_id, "security": security_level}
    headers = { 'content-type': 'application/x-www-form-urlencoded', 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        print ("[i] URL: %s/DVWA.login.php" % target)
        print ("[i] Data: %s" % data)
        print ("[i] Cookie: %s" % cookie)
        r = requests.post( url, data=data, cookies=cookie, headers=headers, verify=False, allow_redirects=False)
    except:
        print ("login failed, quiting")
        sys.exit(-1)

    if r.headers["Location"] != 'index.php':
        print ("[-] Login Failed")
        exit()
    
    print ("[+] Logged in Successfully")
    return True


# Get initial CSRF token
session_id, user_token = csrf_token()

# Login to web app
dvwa_login(session_id, user_token)