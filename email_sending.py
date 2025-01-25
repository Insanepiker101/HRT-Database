import smtplib
import ssl


def send_pass_rst(email, link):
    email_message = """\
Subject: Password Reset

Password Reset Link Below\

{}
""".format(link)
    send_email(email, email_message)


def send_pass_reg(email, link, key):
    email_message = """\
Subject: GSMP Register

Register Link Below\

{}

Key is below

{}
""".format(link, key)
    send_email(email, email_message)


def send_email(rec_email, message):
    port = 465  # For SSL
    password = 'syrp nxec ozkd baiq'
    sender_email = "gsmp.micro@gmail.com"

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, rec_email, message)


