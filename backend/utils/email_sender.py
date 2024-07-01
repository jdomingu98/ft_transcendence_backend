import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend import settings


class EmailSender:
    def __init__(self):
        self.SMTP_SERVER = settings.SMTP_SERVER
        self.PORT = settings.SMTP_PORT
        self.SENDER_EMAIL = settings.SMTP_EMAIL
        self.PASSWORD = settings.SMTP_PASSWORD
        self.context = ssl.create_default_context()

    def send_email_html(self, receiver_email, subject, html):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.SENDER_EMAIL
        message["To"] = receiver_email
        message.attach(MIMEText(html, "html"))
        self._send_multipart(receiver_email, message)

    def _send_multipart(self, receiver_email, mime):
        with smtplib.SMTP_SSL(self.SMTP_SERVER, self.PORT, context=self.context) as server:
            server.login(self.SENDER_EMAIL, self.PASSWORD)
            server.sendmail(self.SENDER_EMAIL, receiver_email, mime.as_string())
