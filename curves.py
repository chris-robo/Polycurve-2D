import png
import render
import fancy_render

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
        fancy_render.draw_line_sdf(image,p0[0],p0[1],p1[0],p1[1],1,WHITE)

    # for p0,p1,p2 in zip(points[:-2],points[1:-1],points[2:]):



# render.line_draw(image,100,100,200,200,WHITE)

image = [[BLACK for _ in range(WIDTH)] for _ in range(HEIGHT)]

points = parse_curve("wave.curve")
draw_curves(points)

fancy_render.circle_draw_sdf(image,100,100,40,1.,WHITE)

# render.line_draw(image,220,190,230,220,0xFF0000FF)

png.png_save(f"test.png",image)


