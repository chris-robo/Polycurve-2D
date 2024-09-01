import png
import struct
import math
import random

WIDTH = 600
HEIGHT = 400


def load_obj(filename:str):
    vertices = []
    indices = []
    with open(filename,"r") as f:
        lines = f.readlines()
        for line in lines:
            line_type, *line_data = line.split(" ")
            if line_type == "v":
                vertices.append(tuple(float(d) for d in line_data))
            elif line_type == "f":
                indices.append(tuple(int(d)-1 for d in line_data))
    return vertices, indices

# https://paulbourke.net/dataformats/stl/
def load_stl_binary(filename:str):
    tris = []
    with open(filename,"rb") as f:
        header = f.read(80)
        # assert header.startswith(b"binary stl file")
        triangle_count = struct.unpack("<L",f.read(4))[0]
        for _ in range(triangle_count):
            triangle_data = struct.unpack("<12f2B",f.read(50))
            triangle = triangle_data[3:12]
            tris.append(triangle)
    return tris

def set_pixel(pixels,x,y,color):
    if x in range(WIDTH) and y in range(HEIGHT):
        pixels[y][x] = color


def line_draw(pixels,x0,y0,x1,y1,color):

    # make x left to right
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1-x0
    dy = y1-y0

    a = y0-y1
    b = x1-x0
    c = x0*y1 - x1*y0

    if dy > 0:
        if dx > dy:
            # first octant
            y = y0
            for x in range(x0,x1+1):
                if a*x + b*y + c < 0:
                    y += 1
                set_pixel(pixels,x,y,color)
        else:
            # second octant
            x = x0
            for y in range(y0,y1+1):
                if a*x + b*y + c > 0:
                    x += 1
                set_pixel(pixels,x,y,color)
    else:
        if dx > -dy:
            # eigth octant
            y = y0
            for x in range(x0,x1+1):
                if a*x + b*y + c > 0:
                    y -= 1
                set_pixel(pixels,x,y,color)
        else:
            # seventh octant
            x = x1
            for y in range(y1,y0+1):
                if a*x + b*y + c > 0:
                    x -= 1
                set_pixel(pixels,x,y,color)


def scanline_fill(pixels,y,x0,x1,color):
    if not y in range(HEIGHT):
        return

    x0 = max(0,x0)
    x1 = min(WIDTH,x1+1)

    for x in range(x0,x1):
        pixels[y][x] = color

def circle_draw(pixels,cx,cy,r,color):
    x = r
    y = 0
    while x >= y:
        set_pixel(pixels,cx+x,cy+y,color)
        set_pixel(pixels,cx+y,cy+x,color)
        set_pixel(pixels,cx-y,cy+x,color)
        set_pixel(pixels,cx-x,cy+y,color)
        set_pixel(pixels,cx-x,cy-y,color)
        set_pixel(pixels,cx-y,cy-x,color)
        set_pixel(pixels,cx+y,cy-x,color)
        set_pixel(pixels,cx+x,cy-y,color)

        y += 1
        if x*x + y*y >= r*r:
            x -= 1
    pass

def circle_fill(pixels,cx,cy,r,color):
    x = r
    y = 0
    while x >= y:
        scanline_fill(pixels,cy+y,cx-x,cx+x,color)
        scanline_fill(pixels,cy-y,cx-x,cx+x,color)
        
        scanline_fill(pixels,cy+x,cx-y,cx+y,color)
        scanline_fill(pixels,cy-x,cx-y,cx+y,color)

        y += 1
        if x*x + y*y > r*r:
            x -= 1



def cross2(x0,y0,x1,y1):
    return x0*y1-x1*y0

def tri_area(x0,y0,x1,y1,x2,y2):
    return cross2(x1-x0,y1-y0,x2-x0,y2-y0)/2.

def tri_barycentric(x0,y0,x1,y1,x2,y2,xp,yp):
    D = tri_area(x0,y0,x1,y1,x2,y2)
    if D == 0.:
        D = 1.

    A = tri_area(xp,yp,x1,y1,x2,y2)/D
    B = tri_area(x0,y0,xp,yp,x2,y2)/D
    C = tri_area(x0,y0,x1,y1,xp,yp)/D    
    return A,B,C
    

def tri_fill(pixels,x0,y0,x1,y1,x2,y2,color,do_top_left_rule = True):
    xmin = min(x0,x1,x2)-10
    xmax = max(x0,x1,x2)+10
    ymin = min(y0,y1,y2)-10
    ymax = max(y0,y1,y2)+10
    
    for y in range(ymin,ymax):
        for x in range(xmin,xmax):
            # TODO: use ints only
            bc = tri_barycentric(x0,y0,x1,y1,x2,y2,x,y)
            if all(bc > 0. for bc in bc):
                set_pixel(pixels,x,y,color)
            elif do_top_left_rule and bc[0] == 0 and bc[1] > 0 and bc[2] > 0: # top-left rule
                if y1 == y2 and y0 > y1: # top
                    set_pixel(pixels,x,y,color)
                elif y1 < y2: # left
                    set_pixel(pixels,x,y,color)
            elif do_top_left_rule and bc[0] > 0 and bc[1] == 0 and bc[2] > 0:
                if y2 == y0 and y1 > y2:
                    set_pixel(pixels,x,y,color)
                elif y2 < y0:
                    set_pixel(pixels,x,y,color)
            elif do_top_left_rule and bc[0] > 0 and bc[1] > 0 and bc[2] == 0:
                if y0 == y1 and y2 > y0:
                    set_pixel(pixels,x,y,color)
                elif y0 < y1:
                    set_pixel(pixels,x,y,color)


                
def cross3(x0,y0,z0,x1,y1,z1):
    p2 = (
        y0*z1-y1*z0,
        z0*x1-z1*x0,
        x0*y1-y1*x0,        
    )
    return p2


def obj_test():
    vertices, indices = load_obj("teapot.obj")


    pixels = [[0x000000FF for _ in range(WIDTH)] for _ in range(HEIGHT)]


    def projection_ortho(x,y,z):
        # return int((x+4.)/6. * HEIGHT), int((y+2.)/6. * HEIGHT)
        scale = HEIGHT*0.2
        return int((x+3)*scale), int(y*scale)
        # return int((z+3)*scale), int(y*scale)

    n = len(indices)
    for i,idxs in enumerate(indices):
        p0 = projection_ortho(*vertices[idxs[0]])
        p1 = projection_ortho(*vertices[idxs[1]])
        p2 = projection_ortho(*vertices[idxs[2]])
        print(f"{i+1: 5}/{n: 5}")

        # cross3
        tri_fill(pixels,*p0,*p1,*p2,random.randint(0,0xFFFFFF) << 8 | 0xFF)

    for i,idxs in enumerate(indices):
        p0 = projection_ortho(*vertices[idxs[0]])
        p1 = projection_ortho(*vertices[idxs[1]])
        p2 = projection_ortho(*vertices[idxs[2]])
        print(f"{i+1: 5}/{n: 5}")
        line_draw(pixels,*p0,*p1,0xFFFFFFFF)
        line_draw(pixels,*p1,*p2,0xFFFFFFFF)
        line_draw(pixels,*p2,*p0,0xFFFFFFFF)

    png.png_save("test.png",list(reversed(pixels)))


def projection_ortho(x,y,z):
    scale = 4
    return int(scale*x+250.), int(scale*y+250.)

def stl_test():
    pixels = [[0x000000FF for _ in range(WIDTH)] for _ in range(HEIGHT)]
    triangles = load_stl_binary("Stanford_Bunny_sample.stl")

    for triangle in triangles:
        p0 = projection_ortho(*triangle[0:3])
        p1 = projection_ortho(*triangle[3:6])
        p2 = projection_ortho(*triangle[6:9])
        line_draw(pixels,*p0,*p1,0xFFFFFFFF)
        line_draw(pixels,*p1,*p2,0xFFFFFFFF)
        line_draw(pixels,*p2,*p0,0xFFFFFFFF)

    png.png_save("stl_test.png",pixels)


def tri_test():

    pixels = [[0x000000FF for _ in range(WIDTH)] for _ in range(HEIGHT)]

    circle_fill(pixels,400,100,24,0xFF0000FF)
    circle_draw(pixels,400,100,24,0x00FF00FF)


    # line_draw(pixels,0,200,400,200,0xFF0000FF)
    tri_fill(pixels,120,120,120,200,200,100,0xFFFFFFFF)
    tri_fill(pixels,121,200,171,170,201,100,0x0FFFFFFF)
    # line_draw(pixels,121,200,201,100,0xFFAA00FF)
    cx = 300
    cy = 200
    r = 100
    n = 10

    colors = [
        0x340a35FF,
        0x7e126bFF,
        0xcb99a7FF,
        0xf57e0dFF,
        0x67b047FF,
        0x064069FF,
        0xba5e6bFF,
        0xee9eb3FF,
        0x744d26FF,
        0x5c1655FF,
    ]
    points = [(int(r*math.cos(2*math.pi * i/n))+cx,int(r*math.sin(2*math.pi * i/n))+cy) for i in range(n)]
    for i in range(n):
        # c = random.randint(0,0xFFFFFF) << 8 | 0xFF
        tri_fill(pixels,cx,cy,*points[i-1],*points[i],colors[i])
        # tri_fill(pixels,cx,cy,*points[i-1],*points[i],0xFF + 0xFFFFFFFF - colors[i],do_top_left_rule=False)
        
        # print(f"0x{colors[i]:08X}")
        # png.png_save(f"test{i:02}.png",pixels)

    png.png_save(f"test.png",pixels)


# obj_test()