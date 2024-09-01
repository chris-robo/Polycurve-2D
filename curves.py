import png
import render

WHITE = 0xFFFFFFFF
BLACK = 0x000000FF

WIDTH = 800
HEIGHT = 600


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
    for p0,p1 in zip(points[:-1],points[1:]):
        render.line_draw(image,int(p0[0]),int(p0[1]),int(p1[0]),int(p1[1]),WHITE)

    for p0,p1,p2 in zip(points[:-2],points[1:-1],points[2:]):

        render.circle_draw(image,int(p0[0]),int(p0[1]),int(p0[2]),WHITE)

# points = parse_curve("wave.curve")
# draw_curves(points)

# render.line_draw(image,100,100,200,200,WHITE)

import fancy_render
import math
n  = 20
cx = 200
cy = 200
ro = 100
ri = 9
for j in range(10):
    image = [[BLACK for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for i in range(n):
        fancy_render.draw_line_sdf(image,
            cx+ri*math.cos(i/n*math.pi*2),
            cy+ri*math.sin(i/n*math.pi*2),
            cx+ro*math.cos(i/n*math.pi*2),
            cy+ro*math.sin(i/n*math.pi*2),
            1.+j/4,
            WHITE
        )

    render.circle_draw(image,cx,cy,8,WHITE)
    render.circle_draw(image,cx,cy,6,WHITE)

    render.line_draw(image,220,190,230,220,0xFF0000FF)

    png.png_save(f"test_{j}.png",image)


