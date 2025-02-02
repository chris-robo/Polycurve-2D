
import math


def lerp(x0,y0,x1,y1,x):
    t = (x-x0)/(x1-x0)
    y = y0*(1.-t)+y1*(t-0.)
    return y


def vec2_unit(x,y):
    d = math.hypot(x,y)
    if d == 0.0:
        return 0.0,0.0
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
    # TODO: optimize this
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
            dist,t = point_line_dist(x,y,x0,y0,x1,y1)
            if not math.hypot(x1-x0,y1-y0) or not 0.0 <= t/math.hypot(x1-x0,y1-y0) <= 1.0:
                continue
            d = abs(dist)-(thickness-1.)/2.
            d = max(d,0.)
            d = min(d,1.)
            bgcol = image[y][x]
            image[y][x] = color_lerp(d,color,bgcol)

def point_circle_dist(p,q,cx,cy,r):
    return math.hypot(p-cx,q-cy)-r

def circle_draw_sdf(image,cx,cy,r,thickness,color):
    x0 = cx-r
    x1 = cx+r
    y0 = cy-r
    y1 = cy+r
    xmin = min(x0,x1)
    xmax = max(x0,x1)
    ymin = min(y0,y1)
    ymax = max(y0,y1)
    for y in range(int(ymin)-10,int(ymax)+10):
        for x in range(int(xmin)-10,int(xmax)+10):
            dist = point_circle_dist(x,y,cx,cy,r)
            # if not 0.0 <= t/math.hypot(x1-x0,y1-y0) <= 1.0:
            #     continue
            d = abs(dist)-(thickness-1.)/2.
            d = max(d,0.)
            d = min(d,1.)
            bgcol = image[y][x]
            image[y][x] = color_lerp(d,color,bgcol)
            
def arc_draw_sdf(image,cx,cy,r,x0,y0,x1,y1,thickness,color):
    x0b = cx-r
    x1b = cx+r
    y0b = cy-r
    y1b = cy+r
    xmin = min(x0b,x1b)
    xmax = max(x0b,x1b)
    ymin = min(y0b,y1b)
    ymax = max(y0b,y1b)
    for y in range(int(ymin)-10,int(ymax)+10):
        for x in range(int(xmin)-10,int(xmax)+10):
            dist = point_circle_dist(x,y,cx,cy,r)
            # if not 0.0 <= t/math.hypot(x1-x0,y1-y0) <= 1.0:
            #     continue
            dot0 = (cy-y0)*(x-cx)+(x0-cx)*(y-cy)
            dot1 = (y1-cy)*(x-cx)+(cx-x1)*(y-cy)
            chirality = (x0-cx)*(y1-cy)-(y0-cy)*(x1-cx)
            if chirality*dot0 < 0 or chirality*dot1 < 0:
                continue
            d = abs(dist)-(thickness-1.)/2.
            d = max(d,0.)
            d = min(d,1.)
            bgcol = image[y][x]
            image[y][x] = color_lerp(d,color,bgcol)
            
