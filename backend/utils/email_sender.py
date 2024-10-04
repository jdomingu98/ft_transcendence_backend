import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pynliner
from django.template.loader import render_to_string

from backend import settings


class EmailSender:
    SMTP_SERVER = settings.SMTP_SERVER
    PORT = settings.SMTP_PORT
    SENDER_EMAIL = settings.SMTP_EMAIL
    PASSWORD = settings.SMTP_PASSWORD

    def __init__(self):
        self.context = ssl.create_default_context()

    def send_email_template(self, receiver_email: str, subject: str, template_name: str, context: dict):
        if context is None:
            context = {}
        email_content = render_to_string(template_name, context)
        inliner = pynliner.Pynliner()
        template = inliner.from_string(email_content).run()
        self.send_email_html(receiver_email, subject, template)

    def send_email_html(self, receiver_email: str, subject: str, html: str):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EmailSender.SENDER_EMAIL
        message["To"] = receiver_email
        message.attach(MIMEText(html, "html"))
        self._send_multipart(receiver_email, message)

    def _send_multipart(self, receiver_email: str, mime: MIMEMultipart):
        with smtplib.SMTP_SSL(EmailSender.SMTP_SERVER, EmailSender.PORT, context=self.context) as server:
            server.login(EmailSender.SENDER_EMAIL, EmailSender.PASSWORD)
            server.sendmail(EmailSender.SENDER_EMAIL, receiver_email, mime.as_string())
