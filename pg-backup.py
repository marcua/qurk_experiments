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
    print "args: backup_directory"
    sys.exit()

dir = sys.argv[1]

filename = "%d.sql.gz" % (time.time())
path = "%s/%s" % (dir, filename)
bk_command = "pg_dump -C -U qurkexp qurkexp | gzip > %s" % (path)

print "Backing up..."
os.system(bk_command)

print "Created %s" % (path)
