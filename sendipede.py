#!/usr/bin/python3

import csv
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

config_file = 'config.yml'
address_file = 'addresses.csv'

with open(config_file) as file:
    config = yaml.safe_load(file)

#port = 465  # For SSL
#port = 1025  # Testserver
#smtp_server = "smtp.gmail.com"
#smtp_server = "localhost"
#sender_email = "rbaer@gmx.ch"  # Enter your address
receivers = set() # eliminates duplicate addresses
#password = input("Type your password and press enter: ")

with open(address_file) as file:
    reader = csv.reader(file)
    for email in reader:
        receivers.add(email[0])

context = ssl.create_default_context()
#with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
with smtplib.SMTP(config['server']['name'], config['server']['port']) as server:
    #server.login(config['sender'], config['server']['password'])

    for receiver_email in receivers:
      message = MIMEMultipart("alternative")
      message["Subject"] = "multipart test"
      message["From"] = config['sender']

      # Create the plain-text and HTML version of your message
      text = """\
      Hi,
      How are you?
      Real Python has many great tutorials:
      www.realpython.com"""
      html = """\
      <html>
        <body>
          <p>Hi,<br>
            How are you?<br>
            <a href="http://www.realpython.com">Real Python</a> 
            has many great tutorials.
          </p>
        </body>
      </html>
      """

      # Turn these into plain/html MIMEText objects
      part1 = MIMEText(text, "plain")
      part2 = MIMEText(html, "html")

      # Add HTML/plain-text parts to MIMEMultipart message
      # The email client will try to render the last part first
      message.attach(part1)
      message.attach(part2)

      message["To"] = receiver_email
      server.sendmail(config['sender'], receiver_email, message.as_string())

