# Mailing module
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from main import confidential as cf

def send_mail(subject, message, recipient):
    email_conn = smtplib.SMTP(cf.HOST, cf.PORT)
    email_conn.ehlo()
    email_conn.starttls()
    email_conn.login(cf.MAIL_FROM, cf.MAIL_PW)
    the_msg = MIMEMultipart("alternative")
    the_msg["Subject"] = subject 
    the_msg["From"] = cf.MAIL_FROM
    the_msg["To"] = recipient
    part = MIMEText(message, "html")
    the_msg.attach(part)
    email_conn.sendmail(cf.MAIL_FROM, recipient, the_msg.as_string())
    email_conn.quit()
    return "Mail sent"