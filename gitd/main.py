import imaplib
import json
import time
import sys

conf = "conf.json"

with open(conf, 'r') as f:
    conf = json.load(f)

try:
    email = conf['email']
    password = conf['password']
    interval = 15
    repos = conf['repos']
except KeyError as e:
    print 'Error JSON config missing key:', e
    sys.exit(-1)

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email, password)

    while True:
        for repo in repos:
            mail.select(repo['email_label'])
            msgs = mail.search(None, 'ALL')
            print msgs
#            if msgs is not None:
#                print 'Messages for Label:', repo['email_label']
#                ids = msgs[0][0].split()
#                print ids
#                print mail.fetch(ids[0], '(RFC822)')
#            else:
#                print 'No Messages for Label:', repo['email_label']
        time.sleep(interval)
    # ids = data[0] # data is a list.
    # id_list = ids.split() # ids is a space separated string
    #print id_list

    #latest_email_id = id_list[-1] # get the latest

    #result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID

    #print result
    #print 'Data Length:', len(data)

    #for i in data:
    #    print 'Length element of data:', len(i)
    #    for j in i:
    #        print 'Length of element of i:', len(i)
except imaplib.IMAP4.error as e:
    print 'ERROR'
    print e.message
