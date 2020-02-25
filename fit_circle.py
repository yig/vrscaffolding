from numpy import *

def fit_circle_to_points( points, method = "kasa", save_test_case = False ):
    """
    Given:
        points: a sequence of 2D points as an N-by-2 array.
    Returns:
        A pair of items, `pt, radius`, where `pt` is a 2-array for the center of the circle
        and `radius` is the radius of the circle.
    """
    
    if save_test_case:
        fit_circle_to_points_test_case( points )
    
    ## Points is N-by-2. Make sure it's a Float array with the right shape.
    points = asfarray( points )
    
    assert points.shape[0] >= 2
    assert points.shape[1] == 2
    assert len( points.shape ) == 2
    
    ### We'll fit a line by circle following:
    ### I. Kasa, "A curve fitting procedure and its error analysis", IEEE Trans. Inst. Meas., Vol. 25, pages 8-14, (1976)
    ### From: https://people.cas.uab.edu/~mosya/cl/Kasa.m
    
    mag2 = ( points**2 ).sum(1)
    xy1 = ones( ( len( points ), 3 ) )
    xy1[:,:2] = points
    P = linalg.lstsq( xy1, mag2 )[0]
    
    center = asfarray( [ P[0]/2, P[1]/2 ] )
    radius = sqrt( (P[0]**2 + P[1]**2)/4 + P[2] )
    
    return center, radius

def circle_to_points_quality( points, center, radius ):
    """
    Given:
        points: a sequence of 2D points as an N-by-2 array.
        center: a circle center
        radius: a circle radius
    Returns:
        The average distance from `points` to the circle.
    """
    
    '''
    @assert size( points,1 ) >= 2
    @assert size( points,2 ) == 2
    @assert ndims( points ) == 2
    
    @assert length( center ) == 1
    @assert ndims( center ) == 1
    '''
    
    ## Points is N-by-2. Make sure it's a Float array with the right shape.
    #points = convert( Array{Float64,2}, points )
    
    #return sum( sqrt( sum( ( points - center - radius ).^2, dims = 2 ) ) )
    raise NotImplementedError

def fit_circle_to_points_test_case( points, path = None ):
    if path is None:
        path = "fit_circle_debug.jl"
    
    with open( path, "w" ) as io:
        io.write(
"""
from fit_circle import *
points = %r
print( "points:", points )
segment = fit_circle_to_points( points )
print( segment )
""" % points )
    
    print( "Saved: ", path )

def test_fit_circle_to_points():
    ## center: (.5,.5), radius: sqrt(2)
    curve = asfarray( [[ 0, 0 ], [ 1, 0 ], [ 1, 1 ], [ 0, 1 ]] )
    
    ## center: (0,0), radius: 1
    curve = asfarray( [[ 1, 0 ], [ 0, 1 ], [ -1, 0 ], [ 0, -1 ]] )
    
    ## center: (0,0), radius: 1
    ## A partial circle
    ts = linspace( 0,pi/2, 10 )
    curve = vstack( ( cos(ts), sin(ts) ) ).T
    
    ## curve = random.random( ( 10, 2 ) )
    
    print( "curve:", curve )
    
    center, radius = fit_circle_to_points( curve, save_test_case = True )
    print( "center:", center )
    print( "radius:", radius )
    
    ## sample it 10 times
    ts = linspace( 0, 2*pi, 11 )[:-1]
    sampled = center + radius * vstack( ( cos(ts), sin(ts) ) ).T
    print( "sampled:", sampled )

if __name__ == "__main__":
    test_fit_circle_to_points()
