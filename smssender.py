#! /usr/bin/env python2
# Simple SMS sender.
#
# It retrieves an updated user listing (names and mobile nrs) and message to be sent via git
# and use internal SMS gw to forward.
# It requires a SMS gw (sorry dudes).

import smtplib
import os
import syslog
import sys
import ConfigParser

def logerror(msg):
    syslog.syslog(syslog.LOG_ERR, "SMS SENDER ERROR: %s" % msg)
    
def logging(msg):
    syslog.syslog(syslog.LOG_INFO, "SMS SENDER: %s" % msg)

MYPATH = os.getcwd()
CONFIG = "%s/sms_info.conf" % MYPATH
DESTINATIONS = "%s/destination.csv" % MYPATH
MESSAGE = "%s/message.txt" % MYPATH

# if no file is found, abort
for filename in [CONFIG, DESTINATIONS, MESSAGE]:
    if not os.path.exists(filename):
        logerror("file \"%s\" not found" % filename)
        sys.exit(os.EX_IOERR)

# git update
timestamp = os.fstat(os.open(MESSAGE, os.O_RDONLY)).st_mtime
os.chdir(MYPATH)
os.system("git fetch; git checkout -- message.txt; git checkout -- destination.csv")
new_timestamp = os.fstat(os.open(MESSAGE, os.O_RDONLY)).st_mtime

if not (new_timestamp > timestamp):
    logging("no updates, finishing")
    #sys.exit(os.EX_OK)

print "Found updates"

# get configuration
c = ConfigParser.ConfigParser()
c.read(CONFIG)

smtpgw = c.get("SMS", "smtpgw")
smsgw = c.get("SMS", "smsgw")

# git update