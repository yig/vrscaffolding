import numpy as np
from scipy import linalg
from collections import namedtuple

Point = namedtuple('Point', 'x y')

horizontal = np.array([1.0, 0.0])
vertical   = np.array([0.0, 1.0])
threshold  =  1e-1 # choose random

class Line:
    def __init__(self, curve):
        """
        init line from curve pts

        normal : normal vector
        c      : (x,y).dot(n) + c = 0
        xy     : points
        """
        xi = curve.T[0]
        yi = curve.T[1]
        
        x0, x1 = xi[0], xi[-1]
        y0, y1 = yi[0], yi[-1]
        
        center = np.mean(curve, axis = 0)
        
        # get the covarience matrix and calculate the eigen value and vector
        cov_mat = np.cov(curve, rowvar = 0)
        eig_vals, eig_vects = np.linalg.eig(cov_mat)
        
        # smallest eigen value
        idx = np.argmin(eig_vals)
        
        normal = eig_vects[:,idx]
        c = -np.dot(normal, center)
        a, b = normal

        # n for point count
        n = int(max(abs(x0-x1), abs(y1 - y0)))
        
        # xy: line points
        xy = np.zeros([n, 2])

        # line is horizontal, normal is vertical
        if abs(np.dot(normal, horizontal))  < threshold:
            normal = [0.0, 1.0]
            c = -np.dot(normal, center)
            y = (y0 + y1)/2
            x = np.linspace(x0, x1, n)  
        # line is vertical
        elif abs(np.dot(normal, vertical)) < threshold:
            normal = [1.0, 0.0]
            c = -np.dot(normal, center)
            x = (x0+x1)/2
            y = np.linspace(y0, y1, n)
        # do I need 45 degree or other cases?
        else:
            # none horizontal or vertical
            # but don't want divide a really small number
            if abs(a) < abs(b):
                x = np.linspace(x0,x1,n)
                y = (-c - a * x) / b
            else:
                y = np.linspace(y0, y1, n)
                x = (-c - b * y) / a

        xy[:,0] = x
        xy[:,1] = y
        
        self.normal = normal
        self.c      = c
        self.center = center
        self.xy     = xy
        

    def update( self ):
        """
        We need update during snap

        Returns:
            xy: line points
            (N+1)-by-2 array of x,y points representing a line
        """
        a, b = normal =  self.normal
        center = self.center

        print('update called')

        c = -np.dot(self.normal, center)
                
        x0, y0 = self.xy[0]
        x1, y1 = self.xy[-1]
        
        # n for the count
        n = self.xy.shape[0]

        # I shouldn't get horizontal/vertical here since
        # if near horizontal/vertical, but in case 

        # line is horizontal, normal is vertical
        if abs(np.dot(self.normal, horizontal))  < threshold:
            normal = np.array([0.0, 1.0])
            c = -np.dot(normal, center)
            y = center[1]
            x = np.linspace(x0, x1, n)  
        # line is vertical
        if abs(np.dot(self.normal, vertical)) < threshold:
            normal = np.array([1.0, 0.0])
            c = -np.dot(normal, center)
            x = center[0]
            y = np.linspace(y0, y1, n)
        else:
            # none horizontal or vertical
            # but don't want divide a really small number
            if abs(a) < abs(b):
                x = np.linspace(x0,x1,n)
                y = (-c - a * x) / b
            else:
                y = np.linspace(y0, y1, n)
                x = (-c - b * y) / a

        self.normal = normal
        self.center = center
        self.xy[:,0] = x
        self.xy[:,1] = y

    
    def __str__( self ):
        return "Line: normal({:.2f}, {:.2f}), c({:.2f})".format(self.normal[0], self.normal[1], self.c)
    
    def __repr__( self ):
        return "normal({:.2f}, {:.2f}),c({:.2f})".format(self.normal[0], self.normal[1], self.c)


def snap_line_to_other_lines( line, construction_lines ):
    """
    adjust line to other construction_lines

    Parallel > Perpendicular, do perpendicular first
    """
    # If this line is already vertical or horizontal
    # Maybe I don't want to adjust it according to other lines?
    if  np.array_equal(line.normal, vertical) or np.array_equal(line.normal, horizontal):
        return line

    for existing_line in construction_lines:
        normal_dot_product = abs(np.dot(line.normal,existing_line.normal))
        #print(normal_dot_product)
        if abs(1 - abs(normal_dot_product)) < threshold:
            # print("parallel")
            # parallel
            # can I just use this or do I need to be more careful?
            line.normal = np.array([existing_line.normal[0], existing_line.normal[1]])
        elif normal_dot_product < threshold:
            # since both (-b, a) or (b, -a) perp (a, b)
            # I find the most close one 
            a1, b1 = existing_line.normal
            # counterclockwise 90
            if np.dot(line.normal, [-b1, a1]) >= 0:
                line.normal = np.array([-b1, a1])
            else:
                line.normal = np.array([b1, -a1])
                
    
    # update because normal direction changed
    line.update()

    
    return line


def find_all_intersections_and_midpoints( construction_lines ):
    """
    I may only want to find points when I begin to draw shape 
    find intersections of line along other lines

    a0 x + b0 y = -c0
    a1 x + b1 y = -c1

    mat_a * vec_x = c
    """

    key_points = []

    # for i in range(len(construction_lines)-1, -1, -1):
    #     cur_line = construction_lines[i]
    #     a0, b0 = cur_line.normal
    #     c0 = -cur_line.c
        
    #     points = []
    #     for j in range(i-1, -1, -1):
    #         prev_line = construction_lines[j]
    #         a1, b1 = prev_line.normal
    #         c1 = -prev_line.c

    #         mat_a = np.array([[a0, b0],[a1, b1]])
    #         # print('i, j, linalg.det(mat_a)', i, j, linalg.det(mat_a))
    #         # try with this threshold
    #         # or I need other methods to make sure that I don't computer parallel
    #         if abs(linalg.det(mat_a)) > 1e-10 :
    #             c = np.array([c0, c1])
    #             x, y = linalg.solve( mat_a, c )
    #             # print('i, j, x, y',i, j, x, y)
    #             # is this necessary? 
    #             # I just make sure the point is in line range
    #             # here I just use the canvas size vaugely
    #             if  0 <= x <= 500:
    #                 points.append((int(x), int(y)))
        
    #     print('i = ', i)
    #     print('points = ,', points)

    for i in range(len(construction_lines)):
        cur_line = construction_lines[i]
        a0, b0 = cur_line.normal
        c0 = -cur_line.c

        points = []

        for j in range(len(construction_lines)):
            next_line = construction_lines[j]
            a1, b1 = next_line.normal
            c1 = -next_line.c
            
            mat_a = np.array([[a0, b0],[a1, b1]])
            # try with this threshold
            # or I need other methods to make sure that I don't computer parallel
            if abs(linalg.det(mat_a)) > 1e-10 :
                c = np.array([c0, c1])
                x, y = linalg.solve( mat_a, c )
                # I just make sure the point is in line range
                # here I just use the canvas size vaugely
                if  0 <= x <= 500:
                    points.append( (round(x), round(y)) )
        print('i = ', i)
        print('points = ,', points)

        # find the intersection points of one line 
        # sort them and find the midpoints
        points.sort(key=lambda x:x[0]) #To sort by first element of the tuple
        midpoints = []
        # find the midpoints
        for j in range(len(points)-1):
            p0, p1 = points[j], points[j+1]
            x = (p0[0] + p1[0])/2
            y = (p0[1] + p1[1])/2
            midpoints.append( (round(x), round(y)) )
        
        # add the point and mid point
        for point in points:
            if point not in key_points:
                key_points.append(point)
        
        for point in midpoints:
            if point not in key_points:
                key_points.append(point)
        

    return key_points

        

            

