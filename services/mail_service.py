import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from services.email_settings_service import get_email_settings


def send_email(user_id, subject, body):
    config = get_email_settings(user_id)

    if not config:
        raise Exception("Email not configured")

    smtp_server = config.get("smtp_server")
    smtp_port = config.get("smtp_port")
    sender_email = config.get("sender_email")
    sender_password = config.get("sender_password")
    to_email = config.get("to_email")
    cc_email = config.get("cc_email")

    # ✅ CREATE MESSAGE (IMPORTANT)
    msg = MIMEMultipart()

    msg["Subject"] = subject  # ✅ FIX: Subject will now work
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Cc"] = cc_email if cc_email else ""

    # ✅ ATTACH HTML BODY
    msg.attach(MIMEText(body, "html"))

    # ✅ HANDLE MULTIPLE CC EMAILS
    cc_list = []
    if cc_email:
        cc_list = [c.strip() for c in cc_email.split(",") if c.strip()]

    recipients = [to_email] + cc_list

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        server.sendmail(
            sender_email,
            recipients,
            msg.as_string()
        )

        server.quit()

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email failed:", str(e))
        raise e