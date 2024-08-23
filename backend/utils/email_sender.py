import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend import settings


class EmailSender:
    SMTP_SERVER = settings.SMTP_SERVER
    PORT = settings.SMTP_PORT
    SENDER_EMAIL = settings.SMTP_EMAIL
    PASSWORD = settings.SMTP_PASSWORD

    def __init__(self):
        self.context = ssl.create_default_context()

    def send_email_html(self, receiver_email, subject, html):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EmailSender.SENDER_EMAIL
        message["To"] = receiver_email
        message.attach(MIMEText(html, "html"))
        self._send_multipart(receiver_email, message)

    def _send_multipart(self, receiver_email, mime):
        with smtplib.SMTP_SSL(EmailSender.SMTP_SERVER, EmailSender.PORT, context=self.context) as server:
            server.login(EmailSender.SENDER_EMAIL, EmailSender.PASSWORD)
            server.sendmail(EmailSender.SENDER_EMAIL, receiver_email, mime.as_string())
