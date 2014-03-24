import django_includes

from gtav import gtav_properties
from qurkexp.estimation.models import *

urldir = "/media/images/gtav"

def db_save(k, ident, data, gender):
    try:
        i = Item.objects.get(kind=k, ident=ident, data=data)
        return
    except:
        i = Item.objects.create(kind=k, ident=ident, data=data)
        Annotation.objects.create(item=i, prop="gender", val=gender)

def create_items():
    k, created = Kind.objects.get_or_create(name="gtav")
    for prop in gtav_properties.properties:
        p = dict(zip(gtav_properties.columns, prop))
        for idx in xrange(1, p["numimages"]+1):
            ident = "%s_%03d" % (p["personid"], idx)
            data = "%s/%s.jpg" % (urldir, ident)
            db_save(k, ident, data, p["gender"])

if __name__ == "__main__":
    create_items()
