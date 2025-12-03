import os
import smtplib

from email.message import EmailMessage

from app.core.settings import settings

def send_email(to: str, subject: str, body: str, html: bool = False):
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject

    if html:
        msg.set_content(body, subtype="html")
    else:
        msg.set_content(body)

    try:
        # Verbindung direkt mit Host/Port aufbauen
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()  # Handshake mit Server
            if settings.EMAIL_TLS:
                server.starttls()
                server.ehlo()  # erneuter Handshake nach TLS
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Fehler beim Mailversand: {e}")
        raise
