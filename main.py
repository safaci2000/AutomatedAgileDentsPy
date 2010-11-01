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

    print configM['email']['to']
    
    msg['From'] = configM['email']['from']
    msg['To'] = configM['email']['to'] 
    msg['Cc'] = configM['email']['cc']
    msg['Bcc'] = configM['email']['bcc']
    msg['Subject'] =  configM['email']['bcc'] + str(date)

    part1=MIMEText(body ,'plain') 
    msg.attach(part1)
    s = smtplib.SMTP(configM['email']['smtp_host'])
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

    return
    

def post(msg):
    status = api.GetUserTimeline(user)
    print [i.text for i in status]
    api.PostUpdate(msg)

def getData():
    ###TODO:  FIX date logica.
    now = datetime.datetime.now()
    ##zero out the hours
    now = datetime.datetime(now.year, now.month, now.day)
    #yesterday= datetime.datetime(now.year,now.month, (now.day - 1))
    yesterday= now

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
        email['from'] = config.get('Email','from')
        email['to'] = config.get('Email','to')
        email['cc'] = config.get('Email','cc')
        email['bcc'] = config.get('Email','bcc')
        email['subject'] = config.get('Email','subject')
        configM['email'] = email
    except:
        print("Could not read psql configuration... terminating")
        sys.exit(1)


def main():
    global user
    global password
    global host
    global configM
    global report

    configM= {}

    p = optparse.OptionParser()
    p.add_option('--user', '-u', default="user",help="Twitter/Identi.ca user name")
    p.add_option('--password', '-p', default="password",help="Twitter/Identi.ca password")
    p.add_option('--host', '-H', default="localhost",help="API URL")
    p.add_option('--config','-c',default="config.ini",help="Configuration file specifying misc defaults (mostly transport / email related)")
    p.add_option('--report','-r',action="store_true", default=False,help="Only report, do not send email.")

    options, arguments = p.parse_args()

    user=options.user
    password=options.password
    host=options.host
    report=options.report

    processConfig(options.config)
    if(password == "password"):
        password=getpass.getpass("Password: ")

    conn()
    text= getData()
    if(report == True):
        print "send email"
        sendEmail(text)

if __name__ == '__main__':
        main()
