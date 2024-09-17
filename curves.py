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
    if d == 0.0:
        return 0.0,0.0
    return x/d,y/d

def vec2_dot(x0,y0,x1,y1):
    return x0*x1+y0*y1

def vec2_cross(x0,y0,x1,y1):
    return x1*y0-x0*y1

def draw_curves(points,invert_y:bool=False):
    # flip: if true, draw using top left as origin
    # otherwise, draw using bottom left as origin  
    # for p0,p1 in zip(points[:-1],points[1:]):
    #     fancy_render.draw_line_sdf(image,p0[0],p0[1],p1[0],p1[1],1,WHITE)
    if not invert_y:
        points = [(point[0],HEIGHT-point[1],point[2]) for point in points]

    ends = []
    ends.append((points[0][:2]))

    for p0,p1,p2 in zip(points[:-2],points[1:-1],points[2:]):
        x0,y0,_ = p0
        x1,y1,r = p1
        x2,y2,_ = p2
        x10, y10 = vec2_unit(x0-x1, y0-y1)
        x12, y12 = vec2_unit(x2-x1, y2-y1)
        u = x10*x12+y10*y12
        q = r/math.sqrt(1.-u*u)
        xc = q*(x10+x12)+x1
        yc = q*(y10+y12)+y1
        # fancy_render.circle_draw_sdf(image,xc,yc,r,1.,WHITE)
        dist = q*math.sqrt((x10+x12)**2+(y10+y12)**2+(x10*x12+y10*y12)**2-1.)
        start_pt = (x1+x10*dist,y1+y10*dist)
        end_pt   = (x1+x12*dist,y1+y12*dist)
        ends.append(start_pt)
        ends.append(end_pt)

        fancy_render.arc_draw_sdf(image,xc,yc,r,*start_pt,*end_pt,STROKE_WEIGHT,WHITE)

    ends.append((points[-1][:2]))
    
    for a,b in zip(ends[::2],ends[1::2]):
        fancy_render.draw_line_sdf(image,*a,*b,STROKE_WEIGHT,0xFF0000FF)


def curve_is_closed(curve):
    return curve[0] == curve[-1]

def curve_area(curve):
    poly_area = 0
    for arc_base_a,b in zip(curve,curve[1:]+[curve[0]]):
        poly_area += arc_base_a[1]*b[0]-arc_base_a[0]*b[1]
    print(f"poly_area\t{poly_area:-6.4f}")

    # ends = []
    # ends.append((points[0][:2]))
    # define arc base area as the area of the polygon that is removed to accomodate the arc area.
    arc_base_area = 0
    arc_area = 0
    for p0,p1,p2 in zip(points[:-2],points[1:-1],points[2:]):
        x0, y0, _ = p0
        x1, y1, r = p1
        x2, y2, _ = p2
        x10, y10 = vec2_unit(x0-x1, y0-y1)
        x12, y12 = vec2_unit(x2-x1, y2-y1)
        u = x10*x12+y10*y12
        q = r/math.sqrt(1.-u*u)
        # xc = q*(x10+x12)+x1
        # yc = q*(y10+y12)+y1
        # fancy_render.circle_draw_sdf(image,xc,yc,r,1.,WHITE)
        dist = q*math.sqrt((x10+x12)**2+(y10+y12)**2+(x10*x12+y10*y12)**2-1.)
        # start_pt = (x1+x10*dist,y1+y10*dist)
        # end_pt   = (x1+x12*dist,y1+y12*dist)
        arc_base_a = 2.*q*dist*(y10*(x10+x12)-x10*(y10+y12))
        arc_base_area += arc_base_a
        # print(a)
        arc_angle = math.atan2(x10*y12-x12*y10, x10*x12+y10*y12) # max allowed is 180 deg and its a degenerate case anyways so this shouldnt be out of bounds...
        arc_a = math.pi*r*r*arc_angle/(2.*math.pi)
        arc_area += arc_a
        # print(arc_a)
    print(f"arc_base_area:\t{arc_base_area:-6.4f}")
    print(f"arc_area:\t{arc_area:-6.4f}")

    curve_a = poly_area + arc_base_area + arc_area
    print(f"curve_area:\t{curve_a:-6.4f}")
    return curve_a

def tri_centroid(x0,y0,x1,y1,x2,y2):
    
    pass

image = [[BLACK for _ in range(WIDTH)] for _ in range(HEIGHT)]


def curve_centroid_y(curve):
    # centroid_x = sum(xs*areas)/sum(areas)
    # https://mathworld.wolfram.com/PolygonCentroid.html
    poly_centroid_x = 0
    poly_centroid_y = 0
    poly_area = 0
    for a,b in zip(curve,curve[1:]+[curve[0]]):
        poly_area_delta = (a[1]*b[0]-a[0]*b[1])/2.
        poly_centroid_dx = poly_area_delta*(a[0]+b[0])/3.
        poly_centroid_dy = poly_area_delta*(a[1]+b[1])/3.
        # print(poly_area_delta)
        # print(f"{poly_centroid_dy=}")
        poly_area += poly_area_delta
        poly_centroid_x += poly_centroid_dx
        poly_centroid_y += poly_centroid_dy
    poly_centroid_x /= poly_area
    poly_centroid_y /= poly_area
    # print(f"{poly_area=}")
    # print(f"{poly_centroid_y=}")

    arc_base_centroid_x = 0
    arc_base_centroid_y = 0
    arc_base_area = 0

    arc_centroid_x = 0
    arc_centroid_y = 0
    arc_area = 0

    for p0,p1,p2 in zip(points[:-2],points[1:-1],points[2:]):
        x0, y0, _ = p0
        x1, y1, r = p1
        x2, y2, _ = p2
        x10, y10 = vec2_unit(x0-x1, y0-y1)
        x12, y12 = vec2_unit(x2-x1, y2-y1)
        u = x10*x12+y10*y12
        q = r/math.sqrt(1.-u*u)
        xc = q*(x10+x12)+x1
        yc = q*(y10+y12)+y1
        # fancy_render.circle_draw_sdf(image,xc,yc,r,1.,WHITE)
        dist = q*math.sqrt((x10+x12)**2+(y10+y12)**2+(x10*x12+y10*y12)**2-1.)
        start_pt = (x1+x10*dist,y1+y10*dist)
        end_pt   = (x1+x12*dist,y1+y12*dist)

        # arc_base_area_delta = -dist*dist*(x12*y10-x10*y12) # this is probably wrong...
        # arc_base_area += arc_base_area_delta
        arc_base_area_delta = q*dist*(y10*(x10+x12)-x10*(y10+y12))
        print(f"{arc_base_area_delta=}")
        arc_base_area += arc_base_area_delta

        left_tri_centroid  = (xc+x1+(x1+x10*dist))/3., (yc+y1+(y1+y10*dist))/3.
        right_tri_centroid = (xc+x1+(x1+x12*dist))/3., (yc+y1+(y1+y12*dist))/3.
        
        arc_base_centroid_delta = (left_tri_centroid[0]+right_tri_centroid[0])/2, (left_tri_centroid[1]+right_tri_centroid[1])/2
        arc_base_centroid_x += arc_base_centroid_delta[0]*arc_base_area_delta
        arc_base_centroid_y += arc_base_centroid_delta[1]*arc_base_area_delta
        
        # print(arc_base_centroid)
        # fancy_render.circle_draw_sdf(image,arc_base_centroid[0],HEIGHT-arc_base_centroid[1],4,2,0xFF0000FF)

        # print(a)
        arc_angle = math.atan2(x10*y12-x12*y10, x10*x12+y10*y12) # max allowed is 180 deg and its a degenerate case anyways so this shouldnt be out of bounds...
        print(f"{arc_angle=}")
        arc_area_delta = math.pi*r*r*arc_angle/(2.*math.pi)
        arc_area += arc_area_delta

        # arc_th = math.asin((xc-x1)*(yc-y0)-(xc-x0)*(yc-y1))
        xc1, yc1 = vec2_unit(x1-xc,y1-yc)
        arc_centroid_dist = (2*r*math.sin(arc_angle))/(3*arc_angle)
        arc_centroid_delta = xc+xc1*arc_centroid_dist,yc+yc1*arc_centroid_dist
        # arc_area += arc_area_delta
        arc_centroid_x += arc_area_delta*arc_centroid_delta[0]
        arc_centroid_y += arc_area_delta*arc_centroid_delta[1]

        # print(arc_a)

    arc_base_centroid_x /= arc_base_area
    arc_base_centroid_y /= arc_base_area

    arc_centroid_x /= arc_area
    arc_centroid_y /= arc_area

    total_area = poly_area+arc_base_area+arc_area
    
    # Testing:
    # poly_centroid_x = 0
    # poly_centroid_y = 0
    print(f"{poly_centroid_x=}")
    print(f"{poly_centroid_y=}")
    # arc_base_centroid_x = 0
    # arc_base_centroid_y = 0
    print(f"{arc_base_centroid_x=}")
    print(f"{arc_base_centroid_y=}")
    # arc_centroid_x = 0
    # arc_centroid_y = 0
    print(f"{arc_centroid_x=}")
    print(f"{arc_centroid_y=}")

    print(f"{poly_area    =: }")
    print(f"{arc_base_area=: }")
    print(f"{arc_area     =: }")
    centroid_x = (poly_area*poly_centroid_x+arc_base_area*arc_base_centroid_x+arc_area*arc_centroid_x)/total_area
    centroid_y = (poly_area*poly_centroid_y+arc_base_area*arc_base_centroid_y+arc_area*arc_centroid_y)/total_area
    fancy_render.circle_draw_sdf(image,centroid_x,HEIGHT-centroid_y,6,2,0x00FF00FF)
    # TODO: Test Thouroughly!!!!!!!
    return centroid_x,centroid_y
# render.line_draw(image,100,100,200,200,WHITE)

# points = parse_curve("asym.txt")
# points = parse_curve("poly.curve")
points = parse_curve("circle.txt")
draw_curves(points)
if curve_is_closed(points):
    print("Curve is closed!")
    area = curve_area(points)
    x_height,y_height = curve_centroid_y(points)
    volume = area*y_height*2*math.pi
    print(f"{volume=}")
else:
    print("Curve is not closed.")


# fancy_render.arc_draw_sdf(image,
#                           200,200,90,
#                           400,200,
#                           200,400,
#                           2,WHITE)

# render.line_draw(image,220,190,230,220,0xFF0000FF)

png.png_save(f"test.png",image)
