
import math


def lerp(x0,y0,x1,y1,x):
    t = (x-x0)/(x1-x0)
    y = y0*(1.-t)+y1*(t-0.)
    return y


def vec2_unit(x,y):
    d = math.hypot(x,y)
    return x/d,y/d

def color_lerp(t,c0,c1):
    r0 = ((c0 >> 24) & 0xFF)/255
    g0 = ((c0 >> 16) & 0xFF)/255
    b0 = ((c0 >>  8) & 0xFF)/255
    a0 = ((c0 >>  0) & 0xFF)/255
    
    r1 = ((c1 >> 24) & 0xFF)/255
    g1 = ((c1 >> 16) & 0xFF)/255
    b1 = ((c1 >>  8) & 0xFF)/255
    a1 = ((c1 >>  0) & 0xFF)/255
    
    r = int((r0*(1.-t)+r1*(t-0.))*255)
    g = int((g0*(1.-t)+g1*(t-0.))*255)
    b = int((b0*(1.-t)+b1*(t-0.))*255)
    a = int((a0*(1.-t)+a1*(t-0.))*255)

    c = (r << 24) | (g << 16) | (b <<  8) | (a <<  0)
    return c

def point_line_dist(p,q,x0,y0,x1,y1):
    unit_right_x, unit_right_y = vec2_unit(y1-y0,x0-x1)
    line_unit_x , line_unit_y  = vec2_unit(x1-x0,y1-y0)
    t = (p-x0)*line_unit_x + (q-y0)*line_unit_y
    near_point_x, near_point_y = (t*line_unit_x)+x0,(t*line_unit_y)+y0
    dist = (p-near_point_x)*unit_right_x+(q-near_point_y)*unit_right_y
    return dist, t


def draw_line_sdf(image,x0,y0,x1,y1,thickness,color):
    xmin = min(x0,x1)
    xmax = max(x0,x1)
    ymin = min(y0,y1)
    ymax = max(y0,y1)
    for y in range(int(ymin)-10,int(ymax)+10):
        for x in range(int(xmin)-10,int(xmax)+10):
            bgcol = image[y][x]
            dist,t = point_line_dist(x,y,x0,y0,x1,y1)
            if not 0.0 <= t/math.hypot(x1-x0,y1-y0) <= 1.0:
                continue
            d = abs(dist)-(thickness-1.)/2.
            d = max(d,0.)
            d = min(d,1.)
            image[y][x] = color_lerp(d,color,bgcol)


