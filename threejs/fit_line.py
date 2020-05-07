import numpy as np

x_unit_vec = np.array( [1, 0, 0] )
y_unit_vec = np.array( [0, 1, 0] )
z_unit_vec = np.array( [0, 0, 1] )

horizontal_threshold  = 80 # was 0.1,  may be 10 degre
vertical_threshold    = 10 # was 0.02, may be 10 degree
parallel_threshold    = 15 # was 0.01, maybe also 10 degree
distance_threshold    = 0.05 # 5 cm
epsilon_threshold     = 1e-5


def line_fitting( curve ):
    '''
    Given:
        curve: an (N+1)-by-3 dictionary of x,y,z points representing a polyline
    Returns:
        line: 2 points 
    '''
    n = len(curve)

    xi = [ pt['x'] for pt in curve]
    yi = [ pt['y'] for pt in curve]
    zi = [ pt['z'] for pt in curve]
    
    points = np.zeros([n, 3])

    points[:, 0] = xi
    points[:, 1] = yi
    points[:, 2] = zi

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

    return segment_unrot

def snap_line_to_other_lines( line, construction_lines, snap_points ):
    """
    """
    # first, snap to vertical & horzontial directions
    center = (line[0] + line[1])/2
    angle_between_vertical_line = angel_between_vec( line_dir( line ), y_unit_vec )

    # angle between vertial < 10 degree
    if angle_between_vertical_line < vertical_threshold:
        line[0][0] = line[1][0] = center[0]
        line[0][2] = line[1][2] = center[2]
    # angle between vertial > 80 degree
    elif angle_between_vertical_line > horizontal_threshold :
        line[0][1] = line[1][1] = center[1]
    
    # snap to possible parallel direction
    smallest_angel = None
    smallest_dir = None
    for existing_line in construction_lines:
        angel_between_lines = angel_between_vec( line_dir(line), line_dir(existing_line) )
        if smallest_angel is None or angel_between_lines < smallest_angel :
            smallest_angel = angel_between_lines
            smallest_dir = line_dir(existing_line)
    
    if smallest_dir is not None and smallest_angel < parallel_threshold:
        rotate_line_to_dir_respect_to_p( line, smallest_dir )

    
    result = line.copy()
    best_distance = None
    for i in range(len(snap_points)):
        candidate = line.copy()
        candidate[0] = snap_points[i]
        for j in range(i + 1, len(snap_points)):
            candidate[1] = snap_points[j]
            distance = distance_between_lines_endpoints( candidate, line )
            
            if best_distance is None or distance < best_distance:
                best_distance = distance
                result = candidate.copy()

    return result
                

def generate_snap_points_for_line( line, snap_points ):
    """
    Given:
        line, generate possible snap points for line
    """
    p0, p1 = line
    if not any(np.array_equal(p0, x) for x in snap_points):
        snap_points.append( p0 )
    if not any(np.array_equal(p0, x) for x in snap_points):
        snap_points.append( p1 )
            
    possible_ratio = [0.5, 1.0, 2.0]
    possible_dirs = possible_direction_respect_to_dir( line_dir(line) )
    length = norm( p0 - p1 )
            

    for ratio in possible_ratio:
        for dir in possible_dirs:
            p = p0 + dir * length * ratio
            if not any(np.array_equal(p, x) for x in snap_points):
                snap_points.append( p )
            p = p1 + dir * length * ratio
            if not any(np.array_equal(p, x) for x in snap_points):
                snap_points.append( p )
    
    return snap_points
    




def possible_direction_respect_to_dir( vec ):
    """
    possible directions of vec, now we only generate 
        2 directions: vec, -vec
        + 4 directions: if the vec is horonztial

        This may limit the directions we want to draw
    """

    possible_dirs = [ ]
    possible_dirs.append( vec.copy() )
    possible_dirs.append( -vec.copy() )

    a, b, c = vec

    # vec has already been snapped, so it should be perfectly horizontal or vertical
    # If it's horizontal, we know perpendicular directions (y axis and horizontal plane perpendicular).

    # vec horonztial
    # if angel_between_vec(vec, y_unit_vec) > 85 :
    if abs( np.dot( vec, y_unit_vec) ) < epsilon_threshold:
        possible_dirs.append( np.array( [-c, 0, a] ) )
        possible_dirs.append( np.array( [c, 0, -a] ) )
        possible_dirs.append( y_unit_vec.copy() )
        possible_dirs.append( -y_unit_vec.copy() )
    # vertical
    # elif angel_between_vec(vec, y_unit_vec) < 5:
    #     possible_dirs.append( x_unit_vec.copy() )
    #     possible_dirs.append( -x_unit_vec.copy() )
    #     possible_dirs.append( z_unit_vec.copy() )
    #     possible_dirs.append( -z_unit_vec.copy() )

    return possible_dirs

def norm(v):
    """
    Given: 
        v : vec or line 
        vec: np.array( [a, b, c] )
        line: np.array([ [a, b, c]
                         [d, e, f] ])
    Return:
        l2 norm of vec or line
    """
    if v.shape == (3,):
        return np.linalg.norm(v)
    else:
        return np.linalg.norm(v[0] - v[1])

def normalize_vec(v):
    """
    normalize vector
    """
    length = norm(v)
    assert length > 0
    return v / length

def line_dir(l):
    """
    Given: 
        line 
    Return:
        normalized line direction vector
    """
    return normalize_vec(l[0] - l[1])

def angel_between_vec( v1, v2 ):
    """
    Given: 
        v1, v2
    Return:
        angel between v1 and v2
        in [0, 90]
    """
    v1_vec = normalize_vec(v1)
    v2_vec = normalize_vec(v2)
    cos_theta = np.dot(v1_vec, v2_vec)
    
    if cos_theta <= 0:
        cos_theta = -cos_theta

    return np.arccos( min(1, cos_theta)  ) * 180 / np.pi 

def distance_between_lines_endpoints(l1, l2):
    """
    Given:
        l1, l2
    Return:
        endpoints distance 
    """
    p0,p1 = l1
    q0,q1 = l2

    return min( norm(p0-q0) + norm(p1-q1), norm(p1-q0) + norm(p0-q1) )

def rotate_line_to_dir_respect_to_p( line, dir, p = 1 ):
    """
    Given:
        line, dir, p
    Return:
        p = 0, rotate line around to line[0]
        p = 1, rotate line around to midpoint
        p = 2, rotate line around to line[2]
    """
    new_line = line.copy()

    p0, p1 = line
    mid = (p0 + p1)/2

    length = norm( line )

    if p == 0:
        new_line[1] = new_line[0] + length * dir
    elif p == 1:
        new_line[0] = mid - length / 2 * dir
        new_line[1] = mid + length / 2 * dir
    else:
        new_line[0] = new_line[1] - length * dir 
    
    return new_line

def min_dist_between_endpoints(l1, l2):
    p0, p1 = l1
    q0, q1 = l2
    return min( norm(q0 - p0), norm(q1 -p0), norm(q1 - p1), norm(q0 - p1) )
    


