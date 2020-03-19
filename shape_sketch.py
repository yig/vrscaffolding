from __future__ import print_function, division

import util
import fit_line
from scipy import linalg,interpolate
import numpy as np



def incorporate_new_raw_shape_line( state, pts ):
    """
    """
    ### 1. Preprocessing. Find key points
    ### 2. Find closest point with key points along the curve. Delete adjacent repeated values in the closest points.
    ### 2 Snap the fit line to existing construction lines.
    ### 3 Store the snapped line as a new construction line in state.
    
    # resample every 10 pixels or is 10px too big?
    shape_curve = util.resample_line_strip_arc_length( pts, 10 )

    key_points = fit_line.find_all_intersections_and_midpoints( state['construction_lines'] )

    # max_dist: max dist between keypoints 
    max_keypoint_dist = max_dist_between_keypoints(key_points)
    
    closest_key_point_indices = []

    for pt in shape_curve:
        # find the point in key_points that nearest to pt
        key_point_index = closest_point_index_to_point( pt, key_points )
        
        ## Skip points too far away.
        if linalg.norm(pt - key_points[key_point_index]) > max_keypoint_dist/15:
            continue
        ## Skip repeated values
        if len( closest_key_point_indices ) >= 1 and key_point_index in closest_key_point_indices: 
            continue
        closest_key_point_indices.append( key_point_index )
    
    assert( len(closest_key_point_indices) > 0 )

    print(closest_key_point_indices)
    closest_key_points = [ key_points[i] for i in closest_key_point_indices ]


    print('closest_key_points ', closest_key_points)

    # closest_key_points.append(closest_key_points[0])
    n = shape_curve.shape[0]
    xy = np.zeros([n, 2])
    
    # very vague way to determine whether close curve or not
    close_line = linalg.norm(shape_curve[0] -  shape_curve[-1]) < 20
    x, y = fit_spline(closest_key_points, n, close_line)
    xy[:,0] = x
    xy[:,1] = y
    
    return xy
    

def fit_spline( closest_key_points, n, closed = True ):
    """
    Fit the splie 
    """
    if closed == True:
        if closest_key_points[0] != closest_key_points[-1] :
            closest_key_points.append(closest_key_points[0])
        

    x = [pt[0] for pt in closest_key_points]
    y = [pt[1] for pt in closest_key_points]

    '''
    tck,u = interpolate.splprep([x, y], k=3, s=0)
    u = np.linspace(0,1,num=n,endpoint=True) 
    spline = interpolate.splev(u,tck)
    return spline[0], spline[1]
    '''
    
    ## Let's try an interpolating cubic spline.
    spline_evaluator = interpolate.CubicSpline(
        ## We will make the key points evenly spaced.
        np.linspace( 0, 1, num = len( closest_key_points ) ),
        ## The key points are the 2D samples.
        closest_key_points,
        ## Use natural boundary conditions (second derivative = 0 at the endpoints)
        ## if not periodic.
        bc_type = 'periodic' if closed else 'natural'
        )
    ## Sample the spline.
    u = np.linspace(0,1,num=n,endpoint=True)
    ## The result `spline` is n-by-2 dimensional.
    spline = spline_evaluator( u )
    ## We want to return x values, y values, which is the tranpose of `spline`.
    return spline.T


def closest_point_index_to_point(pt, key_points):
    """
    find the pt cloest to key_points
    """
    key_point_index = 0
    key_point_dist  = float('inf') 
    for i in range(len(key_points)):
        if linalg.norm(key_points[i] - pt) < key_point_dist:
            key_point_dist = linalg.norm(key_points[i] - pt)
            key_point_index = i
    return key_point_index

def max_dist_between_keypoints( key_points ):
    """
    maximum distance between key points
    """
    max_keypoint_dist = -float('inf')
    for i in range(len(key_points)):
        for j in range(i+1, len(key_points)):
            dist = linalg.norm(np.array(key_points[j]) - np.array(key_points[i]))
            if max_keypoint_dist < dist :
                max_keypoint_dist = dist
    return max_keypoint_dist

