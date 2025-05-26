import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(recipient_email, subject, html_body, attachments=None):
    """
    Sends a formatted HTML email with optional attachments using Gmail.

    Args:
        recipient_email (str): Recipient's email address.
        subject (str): Email subject.
        html_body (str): HTML-formatted message body.
        attachments (list, optional): List of file paths to attach.
    """

    # Load credentials from .env file
    load_dotenv()
    sender_email = os.getenv("sender_email")
    app_password = os.getenv("app_password")

    if not sender_email or not app_password:
        raise ValueError("Missing EMAIL_ADDRESS or EMAIL_APP_PASSWORD in .env")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach HTML body
    msg.attach(MIMEText(html_body, 'html'))

    # Attach any files
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(file_path)}"'
                    )
                    msg.attach(part)
            except Exception as e:
                print (f"❌ Failed to attach {file_path}: {e}")
                return False

    # Send the email via Gmail's SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        print ("✅ Email sent successfully.")
        return True
    except Exception as e:
        print (f"❌ Failed to send email: {e}")
        return False
