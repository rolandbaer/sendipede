# Sendipede

A Python 3 script for sending a message to multiple receivers, but for each
receiver as an individual message.

With this method the receivers don't see the other receivers name or mail
address without sending the mail with the receiver in the bcc field, what
some mail programs treat as spam indication.

## Usage sample

```
./sendipede.py -c config.yml message.txt -a attachment1 attachment2 -r receivers
```

For a complete list of the parameters call sendipede.py with the parameter -h
or --help.

## File Contents

### Message File

The first line of the message file is used as the subject of the mail.
All following text is used as the mail text.

```
Subject Line
Hi there

This is the message that is sent.

Cheers
Sendipede
```

### Receivers

The receivers file contains the email addresses, one address per line

```
receiver.one@email.com
receiver.two@email.com
receiver.three@email.com
```

### Configuration

The configuration file is in the yaml format. See the sample below:

```
server:
  name: localhost
  port: 1025 # 465 for SSL, 1025 for Testserver
  password: nonexisting
  ssl: true

sender: my@email.com
```

If ssl is set to false there will be also no authentication. Disabling ssl is
only recommended for testing purposes in the local network.
