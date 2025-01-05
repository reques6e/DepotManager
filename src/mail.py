import smtplib

from email.message import EmailMessage
from pydantic import EmailStr
from config import settings


def create_booking_confirmation_template(
    data: str,
    email_to: EmailStr,
):
    email = EmailMessage()

    email['Subject'] = 'Test'
    email['From'] = settings.SMTP_USER
    email['To'] = email_to

    email.set_content(
        f'''
            {data}
        ''',
        subtype='html'
    )
    return email

def send_booking_confirmation_email(
    data: str,
    email_to: EmailStr,
):
    # Для отправки сообщения самому себе
    # email_to = settings.SMTP_USER
    msg_content = create_booking_confirmation_template(data, email_to)

    with smtplib.SMTP_SSL(
        settings.SMTP_HOST, 
        settings.SMTP_PORT
        ) as server:
            server.login(
                settings.SMTP_USER, 
                settings.SMTP_PASS
            )
            server.send_message(msg_content)
