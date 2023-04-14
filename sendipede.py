#!/usr/bin/python3

import argparse
import csv
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

config_file = 'config.yml'
address_file = 'addresses.csv'

receivers = set() # eliminates duplicate addresses

parser = argparse.ArgumentParser(description="Sends a message to multiple receivers, but each message individual")
parser.add_argument("-c", "--config", help="name of the config file (default: %(default)s)", default=config_file)
parser.add_argument("-r", "--receivers", help="name of the file with the receivers addresses, one email address per line (default: %(default)s)", default=address_file)
parser.add_argument("-a", "--attach", help="file(s) to attach", nargs="*")
parser.add_argument("message", help="name of the file containing the message to send. The first line in the file is used as the subject of the mail, the rest as the message itself.")
args = parser.parse_args()

with open(args.config) as file:
  config = yaml.safe_load(file)

with open(args.receivers) as file:
  reader = csv.reader(file)
  for email in reader:
    receivers.add(email[0])

if(config['server']['ssl']):
  context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
  context.load_default_certs()
  server = smtplib.SMTP_SSL(config['server']['name'], config['server']['port'], context=context)
else:
  server = smtplib.SMTP(config['server']['name'], config['server']['port'])

try:
  sender = config['sender']

  if(config['server']['ssl']):
    server.login(sender, config['server']['password'])

  # Create the plain-text and HTML version of your message
  with open(args.message) as file:
    text = file.read()

  texts = text.split('\n', 1)

  for receiver in receivers:
    # message = MIMEMultipart("alternative")
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver

    message["Subject"] = texts[0]

    part1 = MIMEText(texts[1], "plain")
    message.attach(part1)

    if args.attach != None:
      for attachment_name in args.attach:
        with open(attachment_name, "rb") as attachment:
          part = MIMEBase("application", "octet-stream")
          part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
          "Content-Disposition",
          f"attachment; filename= {attachment_name}",
        )

        message.attach(part)

    server.sendmail(sender, receiver, message.as_string())

finally:
  server.close()

