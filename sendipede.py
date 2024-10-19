#!/usr/bin/python3
"""
A script to send messages to multiple recipients, but for each recipient as an
individual message.
"""
__version__ = "1.1.1"

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

DEFAULT_CONFIG_FILE = 'config.yml'
DEFAULT_ADDRESS_FILE = 'addresses.csv'


def load_message(filename: str):
    """Load the message from the given file and return subject and body of the mail message."""
    with open(filename, encoding="utf-8") as _file:
        _text = _file.read()

    _texts = _text.split('\n', 1)
    _subject = _texts[0]
    _body = _texts[1]
    return _subject, _body


def init_parser(config_file: str, address_file: str):
    """Initialize the argument parser and return it."""
    _parser = argparse.ArgumentParser(
        description="Sends a message to multiple receivers, but each message individual")
    _parser.add_argument(
        "-c", "--config", help="name of the config file (default: %(default)s)", \
            default=config_file)
    _parser.add_argument(
        "-r", "--receivers", help="name of the file with the receivers addresses," \
            " one email address per line (default: %(default)s)", default=address_file)
    _parser.add_argument("-a", "--attach", help="file(s) to attach", nargs="*")
    _parser.add_argument(
        "message", help="name of the file containing the message to send. The first " \
            "line in the file is used as the subject of the mail, the rest as the message itself.")
    _parser.add_argument('-V', '--version', help="Show version information and quit.",
                        action='version', version='Sendipede version ' + __version__)
    return _parser


def send_message(subject, body, receivers, args, config):
    """send the message to the given receivers."""
    logging.info("Start sending Session")
    if config['server']['ssl']:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_default_certs()
        server = smtplib.SMTP_SSL(
            config['server']['name'], config['server']['port'], context=context)
    else:
        server = smtplib.SMTP(
            config['server']['name'], config['server']['port'])

    try:
        sender = config['sender']

        if config['server']['ssl']:
            server.login(sender, config['server']['password'])

        for receiver in receivers:
            # message = MIMEMultipart("alternative")
            message = MIMEMultipart()
            message["From"] = sender
            message["To"] = receiver

            message["Subject"] = subject

            part1 = MIMEText(body, "plain")
            message.attach(part1)

            if args.attach is not None:
                append_attachments(args, message)

            try:
                # as we only send to one receiver the result can be ignored
                server.sendmail(sender, receiver, message.as_string())
                logging.info("message sent to %s", receiver)
            except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, \
                    smtplib.SMTPSenderRefused, smtplib.SMTPDataError, \
                    smtplib.SMTPNotSupportedError) as exception:
                logging.error(
                    "%s: %s while sending to %s", type(exception), exception, receiver)

    finally:
        server.close()
        logging.debug("Session closed")

def append_attachments(args, message):
    """append the attachments to the message."""
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

def split_receivers(receivers, session):
    """split the list of receivers into chunks that fit into a mailserver session."""
    return [receivers[i:i + session] for i in range(0, len(receivers), session)]

#load_message, send_message, split_receivers,
def handle_message(args):
    """main function that handles the message."""
    receivers = set()  # eliminates duplicate addresses

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

if __name__ == "__main__":
    parser = init_parser(DEFAULT_CONFIG_FILE, DEFAULT_ADDRESS_FILE)
    arguments = parser.parse_args()

    # initialise logging
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        filename=f"sendipede-{time.strftime('%Y-%m-%d')}.log")

    logging.info("starting Sendipede %s", __version__)
    handle_message(arguments)
    #load_message, send_message, split_receivers,
    logging.info("Sendipede stopped")
