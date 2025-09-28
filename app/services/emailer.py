import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@local")

env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape()
)

def send_email(to: str, subject: str, template: str, context: dict):
    html = env.get_template(template).render(**context)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        if SMTP_USER:
            s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(SMTP_FROM, [to], msg.as_string())
