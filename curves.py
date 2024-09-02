import png
import render
import fancy_render

WHITE = 0xFFFFFFFF
BLACK = 0x000000FF

WIDTH = 800
HEIGHT = 600

STROKE_WEIGHT = 2 # thickness in pixels

def parse_curve(filename):
    with open(filename,"r") as f:
        text = f.read()
    assert len(text) % 24 == 0

    values = [float(text[i:i+8]) for i in range(0,len(text),8)]
    points = [tuple(values[i:i+3]) for i in range(0,len(values),3)]
    return points

import math

def vec2_unit(x,y):
    d=math.hypot(x,y)
    return x/d,y/d

def draw_curves(points):
    # for p0,p1 in zip(points[:-1],points[1:]):
    #     fancy_render.draw_line_sdf(image,p0[0],p0[1],p1[0],p1[1],1,WHITE)

    ends = []
    ends.append((points[0][:2]))

    for p0,p1,p2 in zip(points[:-2],points[1:-1],points[2:]):
        x0,y0,_ = p0
        x1,y1,r = p1
        x2,y2,_ = p2
        n10 = math.hypot(x0-x1,y0-y1)
        n12 = math.hypot(x2-x1,y2-y1)
        x10 = (x0-x1)/n10
        y10 = (y0-y1)/n10
        x12 = (x2-x1)/n12
        y12 = (y2-y1)/n12
        u = x10*x12+y10*y12
        q = r/math.sqrt(1.-u*u)
        xc = q*(x10+x12)+x1
        yc = q*(y10+y12)+y1
        # fancy_render.circle_draw_sdf(image,xc,yc,r,1.,WHITE)
        # TODO: Wtf
        dist = q*math.sqrt((x10+x12)**2+(y10+y12)**2+(x10*x12+y10*y12)**2-1.)
        start_pt = (x1+x10*dist,y1+y10*dist)
        end_pt   = (x1+x12*dist,y1+y12*dist)
        ends.append(start_pt)
        ends.append(end_pt)

        fancy_render.arc_draw_sdf(image,xc,yc,r,*start_pt,*end_pt,STROKE_WEIGHT,WHITE)

    ends.append((points[-1][:2]))
    
    for a,b in zip(ends[::2],ends[1::2]):
        fancy_render.draw_line_sdf(image,*a,*b,STROKE_WEIGHT,0xFF0000FF)

# render.line_draw(image,100,100,200,200,WHITE)

image = [[BLACK for _ in range(WIDTH)] for _ in range(HEIGHT)]

points = parse_curve("poly.curve")
draw_curves(points)
# fancy_render.arc_draw_sdf(image,
#                           200,200,90,
#                           400,200,
#                           200,400,
#                           2,WHITE)

# render.line_draw(image,220,190,230,220,0xFF0000FF)

png.png_save(f"test.png",image)
