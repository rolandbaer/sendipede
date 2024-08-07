#!/usr/bin/python3
"""
A script to send messages to multiple recipients, but for each recipient as an
individual message.
"""
__version__ = "1.1.0"

import argparse
import csv
import time
import logging
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

default_config_file = 'config.yml'
default_address_file = 'addresses.csv'


def load_message(filename: str):
    with open(filename, encoding="utf-8") as _file:
        _text = _file.read()

    _texts = _text.split('\n', 1)
    _subject = _texts[0]
    _body = _texts[1]
    return _subject, _body


def init_parser(config_file: str, address_file: str):
    _parser = argparse.ArgumentParser(
        description="Sends a message to multiple receivers, but each message individual")
    _parser.add_argument(
        "-c", "--config", help="name of the config file (default: %(default)s)", default=config_file)
    _parser.add_argument(
        "-r", "--receivers", help="name of the file with the receivers addresses, one email address per line (default: %(default)s)", default=address_file)
    _parser.add_argument("-a", "--attach", help="file(s) to attach", nargs="*")
    _parser.add_argument(
        "message", help="name of the file containing the message to send. The first line in the file is used as the subject of the mail, the rest as the message itself.")
    _parser.add_argument('-V', '--version', help="Show version information and quit.",
                        action='version', version='Sendipede version ' + __version__)
    return _parser


def send_message(subject, body, receivers, args, config):
    logging.info("Start sending Session")
    if (config['server']['ssl']):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_default_certs()
        server = smtplib.SMTP_SSL(
            config['server']['name'], config['server']['port'], context=context)
    else:
        server = smtplib.SMTP(
            config['server']['name'], config['server']['port'])

    try:
        sender = config['sender']

        if (config['server']['ssl']):
            server.login(sender, config['server']['password'])

        for receiver in receivers:
            # message = MIMEMultipart("alternative")
            message = MIMEMultipart()
            message["From"] = sender
            message["To"] = receiver

            message["Subject"] = subject

            part1 = MIMEText(body, "plain")
            message.attach(part1)

            if args.attach != None:
                for attachment_name in args.attach:
                    with open(attachment_name, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    # Encode file in ASCII characters to send by email
                    encoders.encode_base64(part)

                    attachment_filename = os.path.basename(attachment_name)
                    # Add header as key/value pair to attachment part
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment_filename}",
                    )

                    message.attach(part)

            try:
                result = server.sendmail(sender, receiver, message.as_string())
                logging.info("message sent to %s", receiver)
            except Exception as exception:
                logging.error(
                    "%s: %s while sending to %s", type(exception), exception, receiver)

    finally:
        server.close()
        logging.debug("Session closed")

def split_receivers(receivers, session):
    return [receivers[i:i + session] for i in range(0, len(receivers), session)]

if __name__ == "__main__":
    receivers = set()  # eliminates duplicate addresses

    parser = init_parser(default_config_file, default_address_file)
    args = parser.parse_args()

    # initialise logging
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO, filename="sendipede-{d}.log".format(d=time.strftime("%Y-%m-%d")))

    logging.info("starting Sendipede " + __version__)
    with open(args.config, encoding="utf-8") as file:
        config = yaml.safe_load(file)

    with open(args.receivers, encoding="utf-8") as file:
        reader = csv.reader(file)
        for email in reader:
            receivers.add(email[0])

    subject, body = load_message(args.message)

    logging.info('sending message "%s"', subject)

    if 'session' in config['server'] and config['server']['session'] > 0:
        receivers_chunks = split_receivers(list(receivers), config['server']['session'])
    else:
        receivers_chunks = [list(receivers)]

    for receiver_chunk in receivers_chunks:
        send_message(subject, body, receiver_chunk, args, config)

    logging.info("Sendipede stopped")
