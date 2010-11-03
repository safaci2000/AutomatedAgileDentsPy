#!/usr/bin/python2.7
import twitter
import smtplib
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import mktime

import datetime
import optparse
import getpass
import ConfigParser
import sys
global api
global configM

def sendEmail(body):
    cred= configM['Email'] 
    msg = MIMEMultipart()
    now = datetime.datetime.now()
    date = now.strftime("%m/%d/%Y")

    msg['From'] = cred['from']
    msg['To'] = cred['to'] 
    msg['cc'] = cred['cc']
    msg['bcc'] = cred['bcc']
    msg['Subject'] =  cred['subject'] + " %s"%(str(date))

    part1=MIMEText(body ,'plain') 
    msg.attach(part1)

    try:
        host="%s:%s"%(cred['host'],cred['port'])
        if(cred['ssl']=="True"):
            mail = smtplib.SMTP_SSL(host)
        else:
            mail = smtplib.SMTP(host)

        if(cred['tls'] == "True"):
            mail.starttls()

        if(cred['pass'] != ""):
            mail.login(cred['user'],cred['pass'])
        else:
            print("No logging information provided, skipping smtp auth")
        mail.sendmail(msg['From'], msg['To'], msg.as_string())
        mail.close()

    except:
        print("Failed to send email, here is the intended output:")
        print (body)


def post(msg):
    status = api.GetUserTimeline(user)
    print([i.text for i in status])
    api.PostUpdate(msg)

def getData():
    global configM
    cred=configM['Tweedentica']
    day = 86400
    now = datetime.datetime.now()
    ##zero out the hours
    now = datetime.datetime(now.year, now.month, now.day)
    nows = mktime(now.timetuple())
    if( now.weekday() == 0):
        yesterday= datetime.datetime.fromtimestamp(nows - (day * 3)  )
    else:
        yesterday= datetime.datetime.fromtimestamp(nows - day )

    status = api.GetUserTimeline(cred['user'])
    yesterdayL = []
    todayL = [] 
    for i in status:
        t = datetime.datetime.fromtimestamp(i.created_at_in_seconds ) 
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
    global configM
    cred = configM['Tweedentica']

    api=twitter.Api(username=cred['user'], password=cred['pass'],twitterserver=cred['host'])
    api.SetSource('python')

def processConfig(config_file):
    global configM
    configM= {} # Reset configuration file.
    print("checking config file: %s" %(config_file))
    config = ConfigParser.ConfigParser()

    #Open File
    try:
        config.readfp(open(config_file))
    except:
        print("Configuration file not found")
        sys.exit(2);

    try:
        #read email section.
        email  = {} 
        email['host'] = config.get('Email','smtp_host')
        email['user'] = config.get('Email','smtp_user')
        email['pass'] = config.get('Email','smtp_pass')
        email['port'] = config.get('Email','smtp_port')
        email['from'] = config.get('Email','from')
        email['to'] = config.get('Email','to')
        email['cc'] = config.get('Email','cc')
        email['bcc'] = config.get('Email','bcc')
        email['subject'] = config.get('Email','subject')
        email['ssl'] = config.get('Email','ssl')
        email['tls'] = config.get('Email','tls')
        configM['Email'] = email
    except:
        print("Could not read email configuration... terminating")
        sys.exit(1)

    try:
        #read ident section.
        Tweedentica  = {} 
        Tweedentica['host'] = config.get('Tweedentica','host')
        Tweedentica['user'] = config.get('Tweedentica','user')
        Tweedentica['pass'] = config.get('Tweedentica','pass')
        configM['Tweedentica'] = Tweedentica
    except:
        print("Could not read Tweedentica configuration... terminating")
        sys.exit(1)

    try:
        #read ident section.
        General = {} 
        General['end_day'] = config.get('General','end_day')
        configM['General'] = General
    except:
        print("Could not read General configuration... terminating")
        sys.exit(1)




def main():
    global configM
    global report

    configM= {}

    p = optparse.OptionParser()
    p.add_option('--user', '-u', default="",help="Twitter/Identi.ca user name")
    p.add_option('--password', '-p', default="",help="Twitter/Identi.ca password")
    p.add_option('--host', '-H', default="",help="API URL")
    p.add_option('--config','-c',default="config.ini",help="Configuration file specifying misc defaults (mostly transport / email related)")
    p.add_option('--report','-r',action="store_true", default=False,help="Only report, do not send email.")

    options, arguments = p.parse_args()

    ##Read configuration 
    processConfig(options.config)
    ##if values are overloaded, use data.
    if(options.user != ""):
        configM['Tweedentica']['user'] = options.user
    if(options.password != ""):
        configM['Tweedentica']['password'] = options.password
    if(options.host != ""):
        configM['Tweedentica']['host'] = options.host

    report=options.report

    ##Allows for interactive input of pass
    if(configM['Tweedentica']['pass'] == "" ):
        configM['Tweedentica']['password']=getpass.getpass("Password: ")

    conn()
    
    text= getData()
    if(report == True):
        print(text)
    else:
        print("send email")
        sendEmail(text)

if __name__ == '__main__':
        main()
