#!/usr/bin/env python

"""
Backup script for postgres DB.  This must be run as user postgres.
   type 'gunzip -c filename.gz | psql'
"""

# Don't change anything below this line
import os
import subprocess
import sys
import time

if len(sys.argv) != 2:
    print "args: file_to_load"
    sys.exit()

filename = sys.argv[1]
bk_command = "gunzip -c %s | psql -U qurkexp qurkexp" % (filename)

print "Dropping DB"
os.system("dropdb -U qurkexp qurkexp")
print "Creating DB"
os.system("createdb -U qurkexp qurkexp")
print "Loading DB..."
os.system(bk_command)
print "Loaded %s" % (filename)
