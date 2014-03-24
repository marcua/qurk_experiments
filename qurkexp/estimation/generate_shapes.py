import aggdraw
import Image
import django_includes
from ImageColor import getrgb
from itertools import product
from qurkexp.estimation.models import *

urldir = "/media/images/shapes"
savedir = "..%s" % (urldir)
fill = ["red", "orange", "yellow", "green", "blue", "pink"]
outline = ["red", "orange", "yellow", "green", "blue", "pink"]
shape = ["triangle", "circle", "square", "diamond"]
size_extremes = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
xy = [100, 100]

def draw_image(draw, f, o, s, e):
    midx = int(.5 * xy[0])
    midy = int(.5 * xy[1])
    left = int((1.0/e) * xy[0])
    right = int(((e-1.0)/e) * xy[0])
    top = int((1.0/e) * xy[1])
    bottom = int(((e-1.0)/e) * xy[1])
    pen = aggdraw.Pen(o, .05*sum(xy))
    brush = aggdraw.Brush(f)

    if s == "triangle":
        draw.polygon([midx, top, right, bottom, left, bottom], pen, brush)
    elif s == "circle":
        draw.ellipse([left, top, right, bottom], pen, brush)
    elif s == "square":
        draw.polygon([left, top, right, top, right, bottom, left, bottom], pen, brush)
    elif s == "diamond":
        deform = int(.15*xy[0])
        draw.polygon([midx, top, right-deform, midy, midx, bottom, left+deform, midy], pen, brush)
    else:
        raise Error("Unknown shape: %s" % (shape))

def db_save(k, ident, data, f, o, s, e):
    try:
        i = Item.objects.get(kind=k, ident=ident, data=data)
        return
    except:
        i = Item.objects.create(kind=k, ident=ident, data=data)
        # loop through properties, save them as annotations
        props = [("fill", f), ("outline", o), ("shape", s), ("size", e)]
        for prop, val in props:
            Annotation.objects.create(item=i, prop=prop, val=val)
    
def create_images():
    k, created  = Kind.objects.get_or_create(name="shape")
    for f, o, s, e in product(fill, outline, shape, size_extremes):
        if f == o:
            continue
        ident = "%s_%s_%s_%d" % (f, o, s, e)
        data = "%s/%s.png" % (urldir, ident)
        save = "%s/%s.png" % (savedir, ident)
        
        im = Image.new("RGB", xy, "white")
        draw = aggdraw.Draw(im)
        draw_image(draw, f, o, s, e)
        draw.flush()
        del draw 

        # write to stdout
        im.save(open(save, "w"), "PNG")
#        db_save(k, ident, data, f, o, s, e)

if __name__ == "__main__":
    create_images()
