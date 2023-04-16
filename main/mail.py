# Mailing module
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib

absolute_path = os.path.dirname(__file__)
mail_data_path = os.path.join(absolute_path, "mail_data.txt")

mail_data_list = []
with open(mail_data_path) as f:
    for line in f:
        mail_data_list.append(line.replace("\n",""))

def send_mail(subject, message, recipient):
    email_conn = smtplib.SMTP(mail_data_list[0], mail_data_list[1])
    email_conn.ehlo()
    email_conn.starttls()
    email_conn.login(mail_data_list[2], mail_data_list[3])
    the_msg = MIMEMultipart("alternative")
    the_msg["Subject"] = subject 
    the_msg["From"] = mail_data_list[2]
    the_msg["To"] = recipient
    part = MIMEText(message, "html")
    the_msg.attach(part)
    email_conn.sendmail(mail_data_list[2], recipient, the_msg.as_string())
    email_conn.quit()