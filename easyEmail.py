import os
import json
import smtplib
import imaplib
import email

PASSWD_DIR=os.path.join(os.path.dirname(__file__),"PASSWORD.json")

with open(PASSWD_DIR) as f:
    _PASSWD=json.load(f)
 
SMTP_SERVER="smtp.gmail.com"
SMS_GATEWAY=["txt.att.net","sms.myboostmobile.com","sms.cricketwireless.net","tmomail.net","email.uscc.net","vtext.com"]

IMAP_SERVER="imap.gmail.com"


class EasyEmail:
    _EMAIL_ADDR=_PASSWD['email']['username']
    _EMAIL_PASSWD=_PASSWD['email']['password']
    @staticmethod
    def simpleSend(receiver,subject,body:str=""):
        if isinstance(receiver,str):
            EasyEmail._simpleSendTo1Person(receiver,subject,body)
        elif isinstance(receiver,int):
            EasyEmail._simpleSendTo1Person(str(receiver),subject,body)
        elif isinstance(receiver,list):
            for i in receiver:
                EasyEmail._simpleSendTo1Person(i,subject,body)
        else:
            raise TypeError("only str, int, and list are allowed to be the receiver var")
    @staticmethod
    def receiveAsDic()->dict:
        dic={}
        with imaplib.IMAP4_SSL(IMAP_SERVER) as imap:
            imap.login(EasyEmail._EMAIL_ADDR,EasyEmail._EMAIL_PASSWD)
            imap.select("Inbox")
            _,msgNum=imap.search(None,"ALL")

            for i,num in enumerate(msgNum[0].split()):
                _,data=imap.fetch(num,"(RFC822)")
                
                msg=email.message_from_string(data[0][1].decode())
                content=None
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        content=part.get_payload()

                dic[i]={'from':msg.get('From'),'to':msg.get('To'),'bcc':msg.get('BCC'),'date':msg.get('Date'),'subject':msg.get('Subject'),'content':content}
        
        return dic
    
    @staticmethod
    def receiveAsJson(indent:int=4)->json:
        return json.dumps(EasyEmail.receiveAsDic(),indent=indent)
    @staticmethod
    def receiveAsList()->list:
        return list(EasyEmail.receiveAsDic().values())

        

    @staticmethod
    def _simpleSendTo1Person(receiver:str,subject:str,body:str=""):
        #if phone number, use sms gateway
        if receiver.replace("@","")==receiver:
            smsReceiver=[]
            for i in range(len(SMS_GATEWAY)):
                smsReceiver.append(receiver+"@"+SMS_GATEWAY[i])
            receiver=smsReceiver
        else:
            receiver=[receiver]


        #send
        for i in range(len(receiver)):
            with smtplib.SMTP_SSL(SMTP_SERVER,465) as smtp:
                
                smtp.login(EasyEmail._EMAIL_ADDR,EasyEmail._EMAIL_PASSWD)

                msg=f"Subject: {subject}\n\n{body}"

                smtp.sendmail(EasyEmail._EMAIL_ADDR,receiver[i],msg)
    
    
