from __future__ import print_function, division

from numpy import *
from vecutil.vecutil import *

def unpack( X ):
    '''
    Given a flat numpy array X, returns it as an array of rotations and an array of scales.
    '''
    
    X = asfarray( X )
    
    # There are rotations for all but the first edge and scales for every edge
    # of the curve, so `X` should have an odd number of elements.
    assert len( X ) % 2 == 1
    
    N = len(X)//2
    rotations = X[:N]
    scales = X[N:]
    assert len( rotations )+1 == len( scales )
    
    return rotations, scales

def pack( rotations, scales ):
    return concatenate( rotations, scales )

def gen_X0( curve ):
    return concatenate( ( zeros( len(curve)-2 ), ones( len(curve)-1 ) ) )

def resample_line_strip_num_samples( line_strip, num_samples ):
    '''
    Given:
        line_strip: a sequence of points (length >= 2)
        num_samples: an integer >= 2
    Returns:
        a sequence `num_samples` points evenly spaced along `line_strip`
        according to arc length
    
    tested
    >>> line_strip = [ (0,0), (1,0), (1,1), (0,1), (0,0) ]
    >>> assert allclose( resample_line_strip_num_samples( line_strip, 5 ), line_strip )
    >>> assert allclose( resample_line_strip_num_samples( line_strip, 9 )[::2], line_strip )
    '''
    
    line_strip = asfarray( line_strip )
    ## `line_strip` should have shape N-by-dimension
    assert len( line_strip.shape ) == 2
    assert len( line_strip ) >= 2
    assert num_samples >= 2
    
    ### 1 Compute the fraction of total arc length of each line segment.
    ### 2 Find the line segment containing each 1/N sample points.
    ### 3 Compute the interpolation value between the start and end of the line segment.
    ###   t_desired = t_start + s*( t_end - t_start ) <=> s = ( t_desired - t_start )/( t_end - t_start )
    ### 4 Interpolate the containing line segments accordingly.
    ### 5 Assemble the results.
    
    ### 1
    line_segments = line_strip[1:] - line_strip[:-1]
    lengths = sqrt( ( line_segments**2 ).sum( axis = 1 ) )
    total_length = lengths.sum()
    cumulative_lengths = append( [0], lengths.cumsum() )/total_length
    # print( 'cumulative_lengths:', cumulative_lengths )
    
    ### 2
    ## Drop the first and last element in linspace, which are 0 and 1
    ts = linspace( 0, 1, num_samples )[1:-1]
    # print( 'ts:', ts )
    edge_starts = searchsorted( cumulative_lengths, ts )-1
    assert ( edge_starts >= 0 ).all()
    # print( 'edge_starts:', edge_starts )
    
    ### 3
    edge_interpolation_parameters = (
        ( ts - cumulative_lengths[ edge_starts ] )
        /
        ( cumulative_lengths[ edge_starts+1 ] - cumulative_lengths[ edge_starts ] )
    )
    
    ### 4
    middle = line_strip[ edge_starts ] + edge_interpolation_parameters[:,None]*( line_strip[ edge_starts+1 ] - line_strip[ edge_starts ] )
    
    ### 5
    ## Put the first and last elements back
    resampled = concatenate( ( line_strip[:1], middle, line_strip[-1:] ) )
    
    return resampled

def resample_line_strip_arc_length( line_strip, arc_length ):
    '''
    Given:
        line_strip: a sequence of points (length >= 2)
        arc_length: a positive number (floating point)
    Returns:
        a sequence points evenly spaced along `line_strip`
        whose arc length distance is approximately arc_length
    
    tested
    >>> line_strip = [ (0,0), (1,0), (1,1), (0,1), (0,0) ]
    >>> assert allclose( resample_line_strip_arc_length( line_strip, 1 ), line_strip )
    >>> assert allclose( resample_line_strip_arc_length( line_strip, 0.5 )[::2], line_strip )
    '''
    
    line_strip = asfarray( line_strip )
    ## `line_strip` should have shape N-by-dimension
    assert len( line_strip.shape ) == 2
    assert len( line_strip ) >= 2
    assert arc_length > 0
    
    ### 1 Compute the total length
    ### 2 Round 1 + the total length / arc length to the nearest integer >= 2.
    ###   The 1+ is for the initial point.
    ### 3 Call resample_line_strip_num_samples()
    
    ### 1
    line_segments = line_strip[1:] - line_strip[:-1]
    lengths = sqrt( ( line_segments**2 ).sum( axis = 1 ) )
    total_length = lengths.sum()
    
    ### 2
    num_samples = 1 + total_length / arc_length
    num_samples = max( 2, num_samples )
    
    ### 3
    return resample_line_strip_num_samples( line_strip, num_samples )

def turning_angles_and_lengths_from_curve( curve ):
    '''
    Given:
        curve: an N-by-2 array of x,y points representing a polyline
    Returns:
        turning_angles: an (N-2)-array of turning angles between the N-1 edges of `curve`
        lengths: an (N-1)-array of lengths of the N-1 edges of `curve`
    '''
    
    curve = asfarray( curve )
    # `curve` should be N-by-2
    assert len( curve.shape ) == 2
    assert( curve.shape[1] ) == 2
    assert len( curve ) >= 3
    
    line_segments = curve[1:] - curve[:-1]
    turning_angles = [ angle2D( line_segments[i], line_segments[i+1] ) for i in range( len(line_segments)-1 ) ]
    lengths = sqrt( ( line_segments**2 ).sum( axis = 1 ) )
    
    return turning_angles, lengths

def curve_from_turning_angles_and_lengths( turning_angles, lengths, xy0 = (0,0), dir0 = (1,0) ):
    '''
    Given:
        turning_angles: an (N-2)-array of turning angles between the N-1 edges of `curve`
        lengths: an (N-1)-array of lengths of the N-1 edges of `curve`
        xy0: an optional x,y starting point for the first point of the curve
        dir0: an optional x,y vector direction for the first edge of the curve
    Returns:
        curve: an N-by-2 array of x,y points representing a polyline
    
    NOTE: The optional `xy0` and `dir0` parameters exist, because a curve defined
          in terms of turning angles and lengths is defined up to position and rotation.
    '''
    
    turning_angles = asfarray( turning_angles )
    lengths = asfarray( lengths )
    
    assert len( turning_angles )+1 == len( lengths )
    assert len( turning_angles.shape ) == 1
    assert len( lengths.shape ) == 1
    
    edge_vectors = zeros( ( len( lengths ), 2 ) )
    edge_vectors[0] = dir( dir0 ) * lengths[0]
    for turning_angle_index in range( len( turning_angles ) ):
        edge_vectors[ turning_angle_index+1 ] = dir( edge_vectors[ turning_angle_index ] ) * lengths[ turning_angle_index+1 ]
        edge_vectors[ turning_angle_index+1 ] = rotate2D( edge_vectors[ turning_angle_index+1 ], turning_angles[ turning_angle_index ] )
    
    curve = cumsum( edge_vectors, axis = 0 ) + asfarray( xy0 ).reshape( 1, 2 )
    positioned_curve = zeros( ( len(curve)+1, 2 ) )
    positioned_curve[0] = xy0
    positioned_curve[1:] = curve
    return positioned_curve

def test_turning_angles_and_lengths_conversions():
    ## curve = asfarray( [ ( 0,0 ), ( 1,0 ), ( 1,1 ), ( 0,1 ), ( 0,0 ) ] )
    curve = asfarray( [ ( 0,0 ), ( 2,0 ), ( 2,1 ), ( 0,1 ), ( 0,0 ) ] )
    ## curve = random.random( ( 10, 2 ) )
    print( curve )
    
    tas, ls = turning_angles_and_lengths_from_curve( curve )
    print( "Turning angles:", tas )
    print( "Lengths:", ls )
    
    curve2 = curve_from_turning_angles_and_lengths( tas, ls, xy0 = curve[0], dir0 = curve[1] - curve[0] )
    print( curve2.round(10) )
    ## print( ( curve - curve2 ).round(10) )
    assert allclose( curve, curve2 )
    print( "Test passed:", allclose( curve, curve2 ) )

def transform_curve( curve, rotations, scales ):
    '''
    Given:
        curve: an (N+1)-by-2 array of x,y points representing a polyline
        rotations: an (N-1)-array of rotations to apply to the N-1 angles between subsequent edges of `curve`
        scales: an N-array of scale factors to apply to the N edges of `curve`
    '''
    
    curve = asfarray( curve )
    tas, ls = turning_angles_and_lengths_from_curve( curve )
    
    rotations = asfarray( rotations )
    scales = asfarray( scales )
    
    assert len( rotations ) == len( tas )
    assert len( scales ) == len( ls )
    
    new_turning_angles = tas + rotations
    new_lengths = ls * scales
    
    new_curve = curve_from_turning_angles_and_lengths(
        new_turning_angles,
        new_lengths,
        # preserve the first point and direction of curve
        xy0 = curve[0],
        dir0 = curve[1] - curve[0]
        )
    return new_curve

def E_closed( curve ):
    curve = asfarray( curve )
    assert len( curve ) > 1
    return mag2( curve[0] - curve[-1] )

def E_smooth( seq ):
    '''
    Given:
        seq: A 1D array of scalars.
    Returns:
        The sum of squared differences between adjacent values.
    '''
    
    seq = asfarray( seq )
    assert len( seq.shape ) == 1
    assert len( seq ) > 1
    
    return ( ( seq[1:] - seq[:-1] )**2 ).sum()

def E_mag( seq ):
    '''
    Given:
        seq: A 1D array of scalars.
    Returns:
        The squared magnitude of its values.
    '''
    
    seq = asfarray( seq )
    assert len( seq.shape ) == 1
    assert len( seq ) > 1
    
    return ( seq**2 ).sum()

def E_total( curve, rotations, scales ):
    w_closed = 1000.
    w_rot = 1./pi
    w_scale = 1./log(2)
    
    transformed_curve = transform_curve( curve, rotations, scales )
    
    total = (
        w_closed * E_closed( transformed_curve )
        +
        w_rot * E_mag( rotations )
        +
        # Take the log() of scales so that scaling up and down by a factor of 2 is
        # penalized the same.
        w_scale * E_mag( log( scales ) )
        )
    return total

def optimize( curve, callback = None ):
    '''
    Returns `rotations, scales` that make the curve close nicely.
    
    Apply the result with `transform_curve( curve, rotations, scales )`.
    '''
    
    def E_closure( X ):
        rotations, scales = unpack( X )
        return E_total( curve, rotations, scales )
    
    import scipy.optimize
    X0 = gen_X0( curve )
    # X0 += .5*random.random( X0.shape )
    print( "Initial rotations:", unpack( X0 )[0] )
    print( "Initial scales:", unpack( X0 )[1] )
    bounds = ( [(None,None)] * (len(X0)//2) ) + ( [(0.01,None)] * (len(X0) - (len(X0)//2)) )
    res = scipy.optimize.minimize( E_closure, X0, bounds = bounds,
        ## Wrap the callback in something that passes it rotations, scales
        callback = ( lambda x: callback( *unpack( x ) ) ) if callback else None
        )
    print( res )
    
    rotations, scales = unpack( res.x )
    return rotations, scales

def optimize_save_test_case( curve, path = None ):
    if path is None: path = 'beautify_debug.py'
    
    with open( path, 'w' ) as f:
        f.write( '''from __future__ import print_function, division
from numpy import *
import beautify

curve = %r

print( curve )

rotations, scales = beautify.optimize( curve )

curve_beautified = beautify.transform_curve( curve, rotations, scales )
print( curve_beautified )
''' % curve )

def test_optimize():
    ## curve = asfarray( [ ( 0,0 ), ( 1,0 ), ( 1,1 ), ( 0,1 ), ( 0,0 ) ] )
    curve = asfarray( [ ( 0,0 ), ( 2,0 ), ( 2,1 ), ( 0,1 ), ( 0,0 ) ] )
    ## curve = random.random( ( 10, 2 ) )
    print( curve )
    
    rotations, scales = optimize( curve )
    print( "Rotations:", rotations )
    print( "Scales:", scales )
    
    curve2 = transform_curve( curve, rotations, scales )
    print( "Resulting curve (rounded to 3 decimal places):" )
    print( curve2.round(3) )
    print( "Difference (rounded to 3 decimal places):" )
    print( ( curve - curve2 ).round(3) )
