import numpy as np

x_vec = np.array( [1, 0, 0] )
y_vec = np.array( [0, 1, 0] )
z_vec = np.array( [0, 0, 1] )

def line_fitting( curve ):
    '''
    Given:
        curve: an (N+1)-by-3 dictionary of x,y,z points representing a polyline
    Returns:

    '''
    n = len(curve)

    xi = [ pt['x'] for pt in curve]
    yi = [ pt['y'] for pt in curve]
    zi = [ pt['z'] for pt in curve]
    
    # print( xi )
    # print( yi )
    # print( zi )
    points = np.zeros([n, 3])

    points[:, 0] = xi
    points[:, 1] = yi
    points[:, 2] = zi
    # print('points:')
    # print(points)

    ### We'll fit a line by PCA.
    ### 1 Center the points.
    ### 2 Project the centered points along the first axis.
    ### 3 Take the min and max projections as the endpoints.
    ### 4 Rotate back.
    
    ### 1
    center = np.mean( points, axis = 0 )
    points = points - center
    
    ### 2
    _, _, Vt = np.linalg.svd( points )
    curve_rot = Vt[0,:] @ points.T
    
    ### 3
    first = curve_rot.min()
    last = curve_rot.max()
    
    ### 4
    segment_unrot = np.asfarray( [ Vt[0,:] * first, Vt[0,:] * last ] )
    segment_unrot += center

    # snap it to vertical
    line_dir = normalize_vec(segment_unrot[1] - segment_unrot[0])
    # line_dir_x = abs( line_dir[0] )
    line_dir_y = abs( line_dir[1] )
    # line_dir_z = abs( line_dir[2] )
    # print( 'line_dir_x ', line_dir_x )
    print( 'line_dir_y ', line_dir_y )
    # print( 'line_dir_z ', line_dir_z )

    # dot product does not do good than this vector component check 
    if 1 - line_dir_y < 1e-2:
        print( line_dir_y )
        print( 'vertical' )
        # center x and y
        segment_unrot[0][0] = segment_unrot[1][0] = center[0]
        segment_unrot[0][2] = segment_unrot[1][2] = center[2]
    elif line_dir_y < 1e-1:
        print( line_dir_y )
        print( 'horizontal' )
        # make it y[0] = y[1]
        segment_unrot[0][1] = segment_unrot[1][1] = center[1]


    return segment_unrot


def dot_product(v1, v2):
    # cal the angel between 2 directions
    # will only calculate < pi angel
    v1_vec = normalize_vec(v1)
    v2_vec = normalize_vec(v2)
    cos_theta = np.dot(v1_vec, v2_vec)
    
    if cos_theta <= 0:
        cos_theta = -cos_theta

    return cos_theta
        

def normalize_vec(v1):
    length = np.sqrt(np.sum(v1**2))
    assert length > 0
    return v1 / np.sqrt(np.sum(v1**2))
