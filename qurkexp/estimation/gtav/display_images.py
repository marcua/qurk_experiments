from gtav_properties import properties, columns

import os

out = open('out.html', "w+")

for p in properties:
    d = dict(zip(columns, p))
    out.write("""%s (%s) """ % (d["personid"], d["gender"]))
    for idx in xrange(1, 5):#d['numimages']+1):
        fname = "jpgs/%s_%03d.jpg" % (d["personid"], idx)
        out.write("""<img src="%s" />""" % (fname))
        if not os.path.exists(fname):
            print "%s does not exist" % fname
    out.write("""<br><hr><br><br><br>\n""")

out.close()
