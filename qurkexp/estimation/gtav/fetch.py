import os

GTAV_URL = 'http://'

for i in xrange(1,45):
    fname = "ID%02d.zip" % (i)
    os.system('wget %s/%s' % (GTAV_URL, fname))
    os.system('unzip %s' % (fname))

os.system("mv *.bmps bmps")

for fname in filter(lambda x: x.endswith('.bmp'), os.listdir('bmps')):
    command = "gm convert -quality 75 bmps/%s jpgs/%s" % (fname, fname.replace(".bmp", ".jpg"))
    os.system(command)
