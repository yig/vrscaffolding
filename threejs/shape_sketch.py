import fit_line
import numpy as np
from scipy import interpolate

distance_threshold    = 0.05 # 5 cm


def incorporate_new_raw_shape_line( state, curve ):
    """
    """
    ### 1. Preprocessing. Find key points
    ### 2. Find closest point with key points along the curve. Delete adjacent repeated values in the closest points.
    ### 2 Snap the fit line to existing construction lines.
    ### 3 Store the snapped line as a new construction line in state.

    key_points = state['key_points']
    print(key_points)

    n = len(curve)

    xi = [ pt['x'] for pt in curve]
    yi = [ pt['y'] for pt in curve]
    zi = [ pt['z'] for pt in curve]
    
    pts = np.zeros([n, 3])

    pts[:, 0] = xi
    pts[:, 1] = yi
    pts[:, 2] = zi


    closest_key_point_indices = []

    for pt in pts:
        # find the point in key_points that nearest to pt
        key_point_index = closest_point_index_to_point( pt, key_points )
        
        ## Skip points too far away.
        if np.linalg.norm(pt - key_points[key_point_index]) > distance_threshold:
            continue
        ## Skip repeated values
        if len( closest_key_point_indices ) >= 1 and key_point_index in closest_key_point_indices: 
            continue
        closest_key_point_indices.append( key_point_index )
    
    assert( len(closest_key_point_indices) > 0 )

    print(closest_key_point_indices)
    # closest_key_points = [ key_points[i] for i in closest_key_point_indices ]
    # ndarray to list
    closest_key_points = [ key_points[i].tolist() for i in closest_key_point_indices ]

    if np.linalg.norm(pts[0] - pts[-1]) < distance_threshold:
        closest_key_points.append( closest_key_points[0] )
 

    print('closest_key_points ', closest_key_points)

    return closest_key_points


def fit_spline( closest_key_points, n, closed = True ):
    """
    Fit the splie 
    """
    if closed == True:
        if closest_key_points[0] != closest_key_points[-1] :
            closest_key_points.append(closest_key_points[0])
        
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
        if np.linalg.norm(pt - key_points[i])< key_point_dist:
            key_point_dist = np.linalg.norm(key_points[i] - pt)
            key_point_index = i
    return key_point_index


