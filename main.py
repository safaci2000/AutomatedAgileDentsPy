#!/usr/bin/python
import twitter
import smtplib
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import datetime
import optparse
import getpass
import ConfigParser
global user
global password
global host
global api
global configM

user=''
password=''
host=''


#def sendEmail(to, cc, subject, msg):
def sendEmail(body):
    msg = MIMEMultipart()
    now = datetime.datetime.now()
    date = now.strftime("%m/%d/%Y")

    msg['From'] = 'samirf@wolfram.com'
    msg['To'] = 'r-alphareports@wolfram.com' 
    msg['Cc'] = 'overmann@wolfram.com'
    msg['Subject'] = "Daily Report for %s"%(date) 
    part1=MIMEText(body ,'plain') 
    msg.attach(part1)
    s = smtplib.SMTP('mail.wolfram.com')
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

    return
    

def post(msg):
    status = api.GetUserTimeline(user)
    print [i.text for i in status]
    api.PostUpdate(msg)

def getData():
    now = datetime.datetime.now()
    ##zero out the hours
    now = datetime.datetime(now.year, now.month, now.day)
    yesterday= datetime.datetime(now.year,now.month, (now.day - 1))

    #yesterday= now -
    #date = now.strftime("%m/%d/%Y")
    status = api.GetUserTimeline(user)
    yesterdayL = []
    todayL = [] 
    for i in status:
        t = datetime.datetime.fromtimestamp(i.created_at_in_seconds ) 
        #msg = "msg '%s' was create at %s"%(i.text, i.created_at)
        msg = "  * %s"%(i.text)
        if (t > yesterday and t < now  ):
            yesterdayL.append(msg)
        if(t > now ):
            todayL.append(msg)
        
    text = "Yesterday:\n"
    for i in yesterdayL:
       text += i + "\n"
    text += "\nToday:\n"
    for i in todayL:
       text += i + "\n"
    return text

def conn():
    global api
    api=twitter.Api(username=user, password=password,twitterserver=host)
    api.SetSource('python')

def processConfig(config_file):
    global configM
    configM= {} # Reset configuration file.
    print "checking config file: %s" %(config_file)
    config = ConfigParser.ConfigParser()
    #Open File

    try:
        config.readfp(open(config_file))
    except:
        print ("Configuration file not found")
        sys.exit(2);
    try:
        #read pgsql section.
        email  = {} 
        email['host'] = config.get('Email','smtp_host')
        email['user'] = config.get('Email','smtp_user')
        email['pass'] = config.get('Email','smtp_pass')
        configM['email'] = email
    except:
        print("Could not read psql configuration... terminating")
        sys.exit(1)


def main():
    global user
    global password
    global host
    global configM

    configM= {}

    p = optparse.OptionParser()
    p.add_option('--user', '-u', default="user",help="Twitter/Identi.ca user name")
    p.add_option('--password', '-p', default="password",help="Twitter/Identi.ca password")
    p.add_option('--host', '-H', default="localhost",help="API URL")
    p.add_option('--config','-c',default="config.ini",help="Configuration file specifying misc defaults (mostly transport / email related)")

    options, arguments = p.parse_args()

    user=options.user
    password=options.password
    host=options.host

    processConfig(options.config)
    if(password == "password"):
        password=getpass.getpass("Password: ")

    conn()
    text= getData()
    sendEmail(text)

if __name__ == '__main__':
        main()
