"""
Given:
    points: a sequence of 2D points as an N-by-2 array.
Returns:
    A pair of items, `pt, radius`, where `pt` is a 2-array for the center of the circle
    and `radius` is the radius of the circle.
"""
function fit_circle_to_points( points; method = "kasa", save_test_case = false )
    if save_test_case
        fit_circle_to_points_test_case( points )
    end
    
    @assert size( points,1 ) >= 2
    @assert size( points,2 ) == 2
    @assert ndims( points ) == 2
    
    ## Points is N-by-2. Make sure it's a Float array with the right shape.
    points = convert( Array{Float64,2}, points )
    
    ### We'll fit a line by circle following:
    ### I. Kasa, "A curve fitting procedure and its error analysis", IEEE Trans. Inst. Meas., Vol. 25, pages 8-14, (1976)
    ### From: https://people.cas.uab.edu/~mosya/cl/Kasa.m
    
    mag2 = sum( points.^2, dims = 2 )
    xy1 = ones( size(points,1), 3 )
    xy1[:,1:2] = points
    P = xy1 \ mag2
    
    center = [ P[1]/2, P[2]/2 ]
    radius = sqrt( (P[1]^2 + P[2]^2)/4 + P[3] )
    
    return center, radius
end

function fit_circle_to_points_test_case( points, path = "" )
    if length(path) == 0
        path = "fit_circle_debug.jl"
    end
    
    open( path, "w" ) do io
        write( io, string(
"""
include("fit_circle.jl")
@show points = """, repr(points), "\n",
"""
@show segment = fit_circle_to_points( points )
""" ) )
    end
    
    println( "Saved: ", path )
end

function test_fit_circle_to_points()
    ## center: (.5,.5), radius: sqrt(2)
    curve = [ 0 0; 1 0; 1 1; 0 1 ]
    
    ## center: (0,0), radius: 1
    curve = [ 1 0; 0 1; -1 0; 0 -1 ]
    
    ## center: (0,0), radius: 1
    ## A partial circle
    ts = range( 0,pi/2, length = 10 )
    curve = hcat( cos.(ts), sin.(ts) )
    
    ## curve = random.random( ( 10, 2 ) )
    
    @show curve
    
    center, radius = fit_circle_to_points( curve, save_test_case = true )
    @show center
    @show radius
end

test_fit_circle_to_points()
