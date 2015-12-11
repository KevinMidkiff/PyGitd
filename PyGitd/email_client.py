"""
Email Client
"""
import imaplib
import traceback
import smtplib
import logging


class EmailClient(object):
    """
    Email client for IMAP and SMTP
    """
    def __init__(self, smpt_server, smtp_port, imap_server, 
            user_email, user_password):
        """
        Constructor
        """
        self.email_address = user_email
        self.inbox_size = 0

    def send_email(self, receipients, subject, body):
        """
        Send Email
        """
        message = \
                "To:{0}\n" + \
                "From:" + self.email_address + \
                "\nSubject:" + subject + \
                "\n\n" + body + "\n"
        self.smtp.sendmail(self.email_addresss, receipients, message)

    def send_receive(self):
        msgs = self.imap_server.search(None, "ALL")
        num_messages = len(msgs[1][0].split())
        


