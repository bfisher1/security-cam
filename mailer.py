import smtplib, ssl
import secrets

port = 465  # For SSL
password = secrets.SENDER_EMAIL_PASSWORD

# Create a secure SSL context
context = ssl.create_default_context()

sender_email = secrets.SENDER_EMAIL

def sendMsg(receiver_email, subject, msg):
    headers = "\r\n".join(["from: " + sender_email,
                        "subject: " + subject,
                        "to: " + receiver_email,
                        "mime-version: 1.0",
                        "content-type: text/html"])

    content = headers + "\r\n\r\n" + msg

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, content)
    server.close()
