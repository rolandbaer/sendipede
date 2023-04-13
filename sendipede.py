#!/usr/bin/python3

import argparse
import csv
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

config_file = 'config.yml'
address_file = 'addresses.csv'

receivers = set() # eliminates duplicate addresses

parser = argparse.ArgumentParser(description="Sends a message to multiple receivers, but each message individual")
parser.add_argument("-c", "--config", help="name of the config file (default: %(default)s)", default=config_file)
parser.add_argument("-a", "--addresses", help="name of the addresses file (default: %(default)s)", default=address_file)
args = parser.parse_args()

with open(args.config) as file:
  config = yaml.safe_load(file)

with open(args.addresses) as file:
  reader = csv.reader(file)
  for email in reader:
    receivers.add(email[0])

context = ssl.create_default_context()
#with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
with smtplib.SMTP(config['server']['name'], config['server']['port']) as server:
  sender = config['sender']
  #server.login(sender, config['server']['password'])

  for receiver in receivers:
    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender

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

    message["To"] = receiver
    server.sendmail(sender, receiver, message.as_string())

